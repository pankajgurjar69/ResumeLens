# Hackathon team plan and demo flow

## Suggested division for five members
1. **Frontend:** landing page, responsive UI, upload interactions and visual polish.
2. **Backend:** Flask routes, validation, SQLite integration and error handling.
3. **Resume processing:** PDF extraction, skill dictionary and alias improvements.
4. **Career logic:** job-role library, matching explanation, roadmap and project suggestions.
5. **Integration & pitch:** testing, demo data, deployment, GitHub, slides and judge Q&A.

## Suggested 24-hour plan
- Hours 0–2: agree on scope, install tools, run starter app.
- Hours 2–6: polish UI and verify PDF upload/extraction.
- Hours 6–10: expand skills and career role data.
- Hours 10–13: test matching and scoring with multiple synthetic resumes.
- Hours 13–16: improve roadmap and report clarity.
- Hours 16–19: integration, mobile responsiveness and error states.
- Hours 19–21: end-to-end testing and deployment attempt.
- Hours 21–24: prepare pitch, backup local demo and judge Q&A.

## Live demo script
1. Open the landing page and explain the problem: students often don't know which skills to build for a target role.
2. Click Analyze My Resume and upload a synthetic PDF resume.
3. Select a target role such as Data Analyst.
4. Explain that the score is a transparent keyword-overlap indicator, not an AI hiring prediction.
5. Show matched skills and missing skills.
6. Open the roadmap and show suggested practice tasks, project ideas and free learning resources.
7. Open History and demonstrate deletion.
8. Close by explaining that the MVP works without a paid AI API and can be extended with semantic matching, OCR and secure accounts later.

## Judge Q&A — suggested honest answers
**Is this a hiring prediction?** No. It is a skill-alignment aid, not a hiring decision or guarantee.

**Is it really AI?** The current MVP uses PDF text extraction and rule-based skill matching. We intentionally made the core transparent and free. Semantic AI can be added later with user consent and a privacy review.

**How do you earn?** Possible future models include college placement-cell licensing, premium career reports or institution dashboards. The hackathon MVP is free and does not process payments.

**How do you protect resumes?** The original PDF is deleted after text extraction; the saved report contains the filename and analysis fields. A production version would add stronger access controls, retention policies and security review.
