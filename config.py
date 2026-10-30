import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-this-secret")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(ROOT, "uploads")
    DATABASE = os.path.join(ROOT, "instance", "resumelens.sqlite3")
    with open(os.path.join(ROOT, "data", "job_roles.json"), encoding="utf-8") as f:
        ROLES = json.load(f)
