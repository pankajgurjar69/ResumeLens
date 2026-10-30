import json
import os
import re

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "skill_aliases.json")
with open(DATA_PATH, encoding="utf-8") as f:
    ALIASES = json.load(f)

def extract_skills(text):
    """Rule-based skill detection. It finds listed terms; it does not judge proficiency."""
    source = text.lower()
    found = []
    for canonical, aliases in ALIASES.items():
        terms = [canonical] + aliases
        for term in terms:
            # Dots are punctuation around ordinary terms ("Python.") but are
            # still included inside the escaped term for names such as Node.js.
            pattern = r"(?<![a-z0-9+#])" + re.escape(term.lower()) + r"(?![a-z0-9+#])"
            if re.search(pattern, source):
                found.append(canonical)
                break
    return sorted(set(found))
