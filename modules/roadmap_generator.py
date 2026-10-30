def build_roadmap(gaps):
    gaps = list(dict.fromkeys(gaps))
    if not gaps:
        return [{"phase": "Portfolio polish", "level": level, "priority": "Continue role practice", "duration": duration,
                 "tasks": tasks} for level, duration, tasks in [
                    ("Beginner", "1 week", ["Choose one existing project and write a clear README.", "Practise explaining the problem and your contribution."]),
                    ("Intermediate", "1–2 weeks", ["Add a useful feature based on the target role.", "Test the feature and document the outcome."]),
                    ("Advanced", "2–3 weeks", ["Improve reliability or performance and describe the tradeoffs.", "Present the finished project as a short case study."])
                 ]]
    roadmap = []
    for skill in gaps[:5]:
        roadmap.extend([
            {"phase": f"{skill}: foundations", "level": "Beginner", "priority": "Start here", "duration": "1 week",
             "tasks": [f"Study the core concepts and official beginner guide for {skill}.", f"Complete two short {skill} exercises and note what you learned."]},
            {"phase": f"{skill}: applied practice", "level": "Intermediate", "priority": "After foundations", "duration": "1–2 weeks",
             "tasks": [f"Build a small feature that uses {skill} in a realistic scenario.", f"Review your work, fix one limitation, and document the decisions."]},
            {"phase": f"{skill}: portfolio evidence", "level": "Advanced", "priority": "After practice", "duration": "2–3 weeks",
             "tasks": [f"Integrate {skill} into a role-relevant project and test edge cases.", f"Publish a concise README showing the outcome and your contribution."]}
        ])
    return roadmap

def build_projects(gaps):
    if not gaps:
        gaps = ["the target role"]
    return [{"title": f"{skill} skills showcase", "description": f"Create a small, useful portfolio project centered on {skill}.",
             "difficulty": "Beginner" if i == 0 else "Intermediate", "technologies": [skill],
             "outcome": "A documented demo with a clear result and setup instructions.", "skills": [skill]}
            for i, skill in enumerate(gaps[:5])]

def build_resources(gaps):
    resources = {
        "Python": ("Python official tutorial", "https://docs.python.org/3/tutorial/"),
        "JavaScript": ("MDN JavaScript guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
        "HTML": ("MDN HTML learning area", "https://developer.mozilla.org/en-US/docs/Learn/HTML"),
        "CSS": ("MDN CSS learning area", "https://developer.mozilla.org/en-US/docs/Learn/CSS"),
        "SQL": ("SQLBolt interactive lessons", "https://sqlbolt.com/"),
        "Git": ("Pro Git book", "https://git-scm.com/book/en/v2"),
        "Excel": ("Microsoft Excel help & learning", "https://support.microsoft.com/excel"),
        "Data Analysis": ("Kaggle Learn", "https://www.kaggle.com/learn"),
        "Machine Learning": ("Google Machine Learning Crash Course", "https://developers.google.com/machine-learning/crash-course"),
        "Communication": ("OpenLearn communication skills", "https://www.open.edu/openlearn/"),
    }
    result = []
    for skill in gaps[:8]:
        if skill in resources:
            title, url = resources[skill]
            result.append({"skill": skill, "title": title, "url": url})
        else:
            result.append({"skill": skill, "title": f"Search free official learning material for {skill}", "url": "https://www.google.com/search?q=free+official+" + skill.replace(" ", "+") + "+tutorial"})
    return result
