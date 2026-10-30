# ResumeLens — 5-minute quick start

1. Install Python 3.10+.
2. Extract this ZIP.
3. Open the extracted `ResumeLens` folder in VS Code.
4. In the terminal:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

5. Visit `http://127.0.0.1:5000`.
6. Select **Analyze resume**, upload a text-based PDF, select a role (or paste a job description), and submit.
7. Open the report to see detected matches, gaps, roadmap, projects and resources.

If `python` is not recognised on Windows, install Python from https://www.python.org/downloads/ and tick **Add Python to PATH** during setup.

If a PDF is scanned like an image, this version may not extract text. Try exporting it as a searchable/text PDF.
