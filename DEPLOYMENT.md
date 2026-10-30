# Free-compatible deployment guide

This project is a Flask web app and includes a `Procfile` for common Python hosting platforms.

## Before deploying
- Push the project to GitHub.
- In the hosting provider, create a new Web Service from the repository.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Set environment variable `SECRET_KEY` to a long random value.
- Keep debug mode off.

## Important about free hosting
Free plans and eligibility change often. Some providers may pause inactive services, limit monthly usage, restrict persistent disks, or remove free web-service tiers. Check the provider's current pricing and storage policy before choosing. This app uses SQLite under `instance/`; on hosts with ephemeral filesystems, the database may reset after redeploy/restart. For a reliable public demo, use a host-supported persistent disk or a managed database that has a currently available free tier.

A provider-generated subdomain (for example, a platform subdomain) may be free if offered on the selected plan. A custom `.com` domain usually requires payment and annual renewal.

## Demo safety
Do not upload real personal resumes to a public hackathon demo unless you have reviewed hosting logs, storage and privacy settings. Use synthetic demo resumes. This MVP does not include login, access control, rate limiting or production-grade security hardening.
