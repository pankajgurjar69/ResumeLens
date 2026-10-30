# ResumeLens — AI Resume Analyzer and Career Roadmap

ResumeLens is an existing Flask application upgraded with optional Gemini advice, resume feedback, skill alignment, staged learning tasks, project/interview suggestions, downloadable PDF reports, and saved roadmap progress. It retains guest mode, optional accounts, SQLite history, and PyMuPDF parsing.

## Project architecture

- `app.py`: Flask pages, uploads, analysis, progress and PDF routes.
- `modules/`: PyMuPDF resume parsing, skill aliases/matching, roadmap generation, and optional Gemini integration.
- `database/db.py`: SQLite schema and additive startup migrations for users, analysis records, and roadmap task progress.
- `templates/`, `static/`: Jinja pages, styling, and quiz interaction.
- `data/`: supported career roles and skill aliases.

## Run locally (Windows)

1. Install Python 3.10+ and extract the ZIP.
2. Open PowerShell in the `ResumeLens` folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Edit `.env` and set a long random `SECRET_KEY`. For live AI features, set `GEMINI_API_KEY` from Google AI Studio. The key stays on the server and is never sent to the browser. `GEMINI_MODEL` defaults to `gemini-2.5-flash`.
4. Start the app with `python app.py` and visit `http://127.0.0.1:5000`.

macOS/Linux: create/activate a virtual environment, install `requirements.txt`, copy `.env.example` to `.env`, configure the values above, and run `python app.py`.

## Features and limits

- Uploads accept PDFs under 5 MB and require a valid PDF header. Text extraction uses PyMuPDF. The temporary upload is deleted after parsing; scanned/image-only documents are not OCR processed.
- Skill matches use canonical skill aliases and an explicit related-skill map, with half credit for related skills. This is a transparent alignment indicator, not a hiring probability or full embedding-based semantic model.
- When `GEMINI_API_KEY` is set, Gemini produces resume-specific review, learning plan, projects, role interview questions, and quiz. The extracted resume text is sent to Google for that request; do not use the feature with sensitive documents unless that data handling is acceptable to you.
- Without a key or when the API is unavailable, deterministic checks still provide section/skill feedback and job alignment; the report clearly labels AI advice unavailable. It does not invent AI responses.
- The report PDF is generated on request. Roadmap task progress is saved per account or guest browser session in SQLite. Sign in to keep it across devices/sessions.
- Startup adds the new analysis columns and progress table without deleting existing records. Back up `instance/resumelens.sqlite3` before upgrades.

## Testing

```powershell
pytest -q
```

Manual checklist: create account and sign in/out; analyze valid and invalid PDFs; analyze a role and custom description; review scores/feedback and AI status; inspect recommendations and interview quiz; download PDF; complete roadmap tasks and reload; revisit history; confirm one user's report cannot be opened from another account.

## Deployment

Use a Python 3.10+ host with persistent disk for the SQLite database. Install from `requirements.txt`, configure `SECRET_KEY`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `FLASK_DEBUG=0`, and run `gunicorn app:app`. Set HTTPS, restrict database/file access, and back up the database. Keep `.env` and real resumes out of version control. Hosting plan limits and persistence vary by provider; verify the provider's current terms before deploying.

## Privacy/security notes

Passwords use Werkzeug hashes; SQL statements are parameterized; each account/guest session has an isolated owner key. The Flask session secret must be changed from the development default for any shared deployment. Add deployment-specific CSRF protection, rate limiting, secure cookie settings, and retention policies before public production use.
