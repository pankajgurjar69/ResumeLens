RELATED = {
    "React": {"JavaScript", "HTML", "CSS"}, "TypeScript": {"JavaScript"},
    "Flask": {"Python"}, "Django": {"Python"}, "FastAPI": {"Python"},
    "Machine Learning": {"Python", "Statistics", "Data Analysis"},
    "Data Analysis": {"SQL", "Excel", "Python"}, "Data Visualization": {"Data Analysis", "Excel"},
    "Node.js": {"JavaScript"}, "PostgreSQL": {"SQL"}, "MySQL": {"SQL"},
    "AWS": {"Docker", "Linux"}, "Communication": {"Leadership", "Project Management"},
}


def compare_skills(resume_skills, required_skills):
    """
    Transparent baseline score:
    - Exact detected skill = matched (1 point)
    - Related/partial detection is not guessed in this version.
    Scores exact canonical/alias matches fully and explicitly related skills partially.
    """
    resume_set = set(resume_skills)
    required = sorted(set(required_skills))
    matched = [skill for skill in required if skill in resume_set]
    partial = [skill for skill in required if skill not in resume_set and bool(RELATED.get(skill, set()) & resume_set)]
    missing = [skill for skill in required if skill not in resume_set and skill not in partial]
    score = round(((len(matched) + 0.5 * len(partial)) / len(required)) * 100) if required else 0
    return {"score": score, "matched": matched, "partial": partial, "missing": missing,
            "required_count": len(required)}
