import os
import re
import secrets
import uuid
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from database.db import (
    init_db, save_analysis, get_analyses, get_analysis, delete_analysis,
    create_user, get_user_by_email, get_user_by_id,
)
from modules.resume_parser import extract_text_from_pdf
from modules.skill_extractor import extract_skills
from modules.job_matcher import compare_skills
from modules.roadmap_generator import build_roadmap, build_projects, build_resources
from modules.ai_advisor import generate_advice, AIUnavailable
from database.db import get_progress, set_progress

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
init_db()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pdf"


def current_owner_key():
    """Each signed-in user or guest browser session gets a separate analysis space."""
    if session.get("user_id"):
        return f"user:{session['user_id']}"
    if not session.get("guest_key"):
        session["guest_key"] = secrets.token_urlsafe(24)
    return f"guest:{session['guest_key']}"


@app.before_request
def load_current_user():
    user_id = session.get("user_id")
    g.current_user = get_user_by_id(user_id) if user_id else None


@app.context_processor
def inject_user_state():
    return {"current_user": getattr(g, "current_user", None), "is_guest": not bool(getattr(g, "current_user", None))}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.current_user:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(name) < 2:
            flash("Please enter your name (at least 2 characters).", "error")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Use a password with at least 8 characters.", "error")
        elif get_user_by_email(email):
            flash("An account with this email already exists. Please sign in.", "error")
        else:
            try:
                user_id = create_user(name, email, generate_password_hash(password))
            except Exception:
                flash("We could not create the account. Please try again.", "error")
                return render_template("register.html")
            session.clear()
            session["user_id"] = user_id
            flash("Your ResumeLens account is ready.", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.current_user:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Email or password is incorrect.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}.", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out. You can continue as a guest.", "success")
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    analyses = get_analyses(current_owner_key())
    latest = analyses[0] if analyses else None
    return render_template("dashboard.html", analyses=analyses[:5], latest=latest, total=len(analyses))


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        file = request.files.get("resume")
        role = request.form.get("role", "").strip()
        custom_jd = request.form.get("job_description", "").strip()
        if not file or not file.filename:
            flash("Please choose a PDF resume first.", "error")
            return redirect(url_for("analyze"))
        if not allowed_file(file.filename):
            flash("Only PDF files are supported.", "error")
            return redirect(url_for("analyze"))
        if not role and not custom_jd:
            flash("Choose a career role or paste a job description.", "error")
            return redirect(url_for("analyze"))
        safe_name = secure_filename(file.filename)
        stored_name = f"{uuid.uuid4().hex}_{safe_name}"
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_name)
        file.save(temp_path)
        try:
            with open(temp_path, "rb") as uploaded:
                if not uploaded.read(5).startswith(b"%PDF-"):
                    raise ValueError("Not a PDF")
            resume_text = extract_text_from_pdf(temp_path)
        except Exception:
            flash("Could not read this PDF. Please try another text-based PDF.", "error")
            return redirect(url_for("analyze"))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if len(resume_text.strip()) < 30:
            flash("Very little text was found. Scanned/image-only PDFs are not supported yet.", "error")
            return redirect(url_for("analyze"))

        found_skills = extract_skills(resume_text)
        if custom_jd:
            target_label = "Custom job description"
            required_skills = extract_skills(custom_jd)
        else:
            target_label = role
            required_skills = app.config["ROLES"].get(role, [])
        if not required_skills:
            flash("We could not identify skills in the selected role/job description. Try adding specific skills.", "error")
            return redirect(url_for("analyze"))

        report = compare_skills(found_skills, required_skills)
        gaps = report["missing"] + report["partial"]
        roadmap = build_roadmap(gaps)
        projects = build_projects(gaps)
        resources = build_resources(gaps)
        review = {"strengths": [], "weaknesses": [], "missing_sections": [], "suggestions": [], "section_feedback": []}
        expected = {"contact": bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", resume_text)),
                    "experience": bool(re.search(r"experience|employment|internship", resume_text, re.I)),
                    "education": bool(re.search(r"education|university|college|degree", resume_text, re.I)),
                    "projects": bool(re.search(r"projects?", resume_text, re.I)),
                    "skills": bool(found_skills)}
        review.update({"strengths": ([f"Relevant skills identified: {', '.join(found_skills[:8])}."] if found_skills else []),
                       "weaknesses": [], "missing_sections": [k.title() for k,v in expected.items() if not v],
                       "suggestions": ["Add measurable outcomes to experience and project bullets.", "Tailor the summary and skills section to the selected target role."],
                       "section_feedback": []})
        focus = gaps[0] if gaps else (found_skills[0] if found_skills else "your strongest skill")
        interview = {"questions": [
            {"type": "Technical", "question": f"Describe how you would learn and apply {focus} to a task in {target_label}.",
             "sample_answer": f"Use a real example: explain the goal, what you tried with {focus}, the result, and what you would improve. If you have not used it yet, say so and describe a small practice plan.",
             "explanation": "A clear, honest example shows your reasoning without overstating experience."},
            {"type": "HR", "question": "Tell me about a time you learned something difficult or responded to feedback.",
             "sample_answer": "Use a specific situation, the action you took, and the result. Mention one lesson you carried forward.",
             "explanation": "Keep the story concise and focus on your own actions and learning."}],
            "quiz": [{"question": f"Which is the strongest way to demonstrate {focus} in a portfolio?",
                      "options": ["List it without examples", "Show a working project, explain your choices, and document the result", "Copy a tutorial unchanged", "Claim expert-level ability"],
                      "answer": 1, "explanation": "A verifiable project plus a clear explanation gives evidence of applied learning."}]}
        ai_status = "Rule-based review; configure Gemini for AI-generated, resume-specific advice."
        resume_score = max(0, min(100, 100 - 12*len(review["missing_sections"]) + min(20, 2*len(found_skills))))
        try:
            advice = generate_advice(resume_text, target_label, report["matched"], report["partial"], report["missing"], roadmap, projects)
            review = {key: advice[key] for key in ("strengths", "weaknesses", "missing_sections", "suggestions", "section_feedback")}
            resume_score = advice["resume_score"]
            roadmap, projects = advice["roadmap"], advice["projects"]
            interview = {"questions": advice["interview"], "quiz": advice["quiz"]}
            ai_status = "AI-generated with Gemini. Review suggestions for accuracy before using them."
        except AIUnavailable as exc:
            ai_status = str(exc)
        record_id = save_analysis(
            owner_key=current_owner_key(), filename=safe_name, target=target_label,
            score=report["score"], matched=report["matched"], partial=report["partial"],
            missing=report["missing"], roadmap=roadmap, projects=projects, resources=resources,
            resume_score=resume_score, review=review, interview=interview, ai_status=ai_status
        )
        return redirect(url_for("result", analysis_id=record_id))
    return render_template("analyze.html", roles=sorted(app.config["ROLES"].keys()))


@app.route("/analysis/<int:analysis_id>")
def result(analysis_id):
    record = get_analysis(analysis_id, current_owner_key())
    if not record:
        flash("Analysis not found in this account or guest session.", "error")
        return redirect(url_for("history"))
    return render_template("analysis.html", item=record)


@app.route("/history")
def history():
    return render_template("history.html", analyses=get_analyses(current_owner_key()))


@app.route("/history/delete/<int:analysis_id>", methods=["POST"])
def remove_history(analysis_id):
    delete_analysis(analysis_id, current_owner_key())
    flash("Analysis record deleted if it belonged to your space.", "success")
    return redirect(url_for("history"))


@app.route("/careers")
def careers():
    return render_template("careers.html", roles=app.config["ROLES"])


@app.route("/roadmap/<int:analysis_id>")
def roadmap(analysis_id):
    record = get_analysis(analysis_id, current_owner_key())
    if not record:
        flash("Analysis not found in this account or guest session.", "error")
        return redirect(url_for("history"))
    progress = get_progress(record["id"], current_owner_key())
    total = sum(len(step.get("tasks", [])) for step in record["roadmap"])
    done = sum(progress.get(f"{i}:{j}", False) for i,step in enumerate(record["roadmap"]) for j,_ in enumerate(step.get("tasks", [])))
    return render_template("roadmap.html", item=record, progress=progress, progress_pct=round(100*done/total) if total else 0)


@app.route("/analysis/<int:analysis_id>/progress", methods=["POST"])
def update_progress(analysis_id):
    owner = current_owner_key()
    record = get_analysis(analysis_id, owner)
    if not record:
        flash("Analysis not found in this account or guest session.", "error")
        return redirect(url_for("history"))
    task_key = request.form.get("task_key", "")
    valid = {f"{i}:{j}" for i,step in enumerate(record["roadmap"]) for j,_ in enumerate(step.get("tasks", []))}
    if task_key in valid:
        set_progress(analysis_id, owner, task_key, request.form.get("completed") == "1")
    return redirect(url_for("roadmap", analysis_id=analysis_id))


@app.route("/analysis/<int:analysis_id>/report.pdf")
def download_report(analysis_id):
    record = get_analysis(analysis_id, current_owner_key())
    if not record:
        flash("Analysis not found in this account or guest session.", "error")
        return redirect(url_for("history"))
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    buffer = BytesIO(); pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter; y = height - 48
    def line(text, size=10, gap=15):
        nonlocal y
        text = str(text).encode("latin-1", "replace").decode("latin-1")
        if y < 55:
            pdf.showPage(); y = height - 48
        pdf.setFont("Helvetica", size); pdf.drawString(48, y, text[:105]); y -= gap
    line("ResumeLens | Career Analysis Report", 18, 28)
    line(f"Target: {record['target']}  |  Date: {record['created_at']}")
    line(f"Resume file: {record['filename']}")
    line(f"Resume quality score: {record.get('resume_score', 0)}/100  |  Job alignment: {record['score']}%", 12, 22)
    for heading, values in (("Strengths", record["review"].get("strengths", [])), ("Areas to improve", record["review"].get("weaknesses", [])),
                            ("Missing sections", record["review"].get("missing_sections", [])), ("Suggestions", record["review"].get("suggestions", [])),
                            ("Matched skills", record["matched"]), ("Partially matched", record["partial"]), ("Skills to learn", record["missing"])):
        line(heading, 13, 18)
        for value in values: line("- " + str(value))
    for entry in record["review"].get("section_feedback", []):
        line(f"{entry.get('section', 'Section')}: {entry.get('feedback', '')}")
    line("Learning roadmap", 13, 18)
    for step in record["roadmap"]:
        line(f"{step.get('phase','')} ({step.get('duration','')})")
        for task in step.get("tasks", []): line("  - " + task)
    line("Recommended projects", 13, 18)
    for project in record["projects"]:
        if isinstance(project, dict):
            line(project.get("title", "Project") + " — " + project.get("description", ""))
            line(f"Difficulty: {project.get('difficulty','')} | Technologies: {', '.join(project.get('technologies', []))}")
            line("Skills: " + ", ".join(project.get("skills", [])) + " | Outcome: " + project.get("outcome", ""))
        else: line(project)
    line("Free learning resources", 13, 18)
    for resource in record["resources"]:
        line(f"{resource.get('skill','')}: {resource.get('title','')} — {resource.get('url','')}")
    pdf.save(); buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"resumelens-report-{analysis_id}.pdf")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        session["privacy_ack"] = True
        flash("Privacy preference saved for this browser session.", "success")
    return render_template("settings.html")


@app.errorhandler(413)
def too_large(_error):
    flash("File is too large. Please upload a PDF under 5 MB.", "error")
    return redirect(url_for("analyze"))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
