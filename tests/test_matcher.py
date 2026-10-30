from modules.job_matcher import compare_skills

def test_score_and_gaps():
    result = compare_skills(["Python", "SQL"], ["Python", "SQL", "Git"])
    assert result["score"] == 67
    assert result["matched"] == ["Python", "SQL"]
    assert result["missing"] == ["Git"]

def test_empty_resume():
    result = compare_skills([], ["Python"])
    assert result["score"] == 0
