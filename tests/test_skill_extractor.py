from modules.skill_extractor import extract_skills

def test_aliases_and_case():
    skills = extract_skills("Built a website with HTML5, CSS3, JS and Python.")
    assert "HTML" in skills
    assert "CSS" in skills
    assert "JavaScript" in skills
    assert "Python" in skills
