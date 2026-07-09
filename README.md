# Vulnerable Notes API — BOLA/IDOR Demonstration

A minimal multi-user Flask notes API built to demonstrate, exploit, and
remediate a Broken Object Level Authorization (BOLA / IDOR) vulnerability.

## ⚠️ Security Disclaimer
This application contains a **deliberate, documented vulnerability** for
educational purposes. It was deployed to a controlled, disposable public
instance solely to demonstrate exploitation and remediation against a live
host. It holds no real user data and the vulnerable version should never be
used to store anything real. If you run it yourself, treat it as a lab, not
a product.

## What This Demonstrates
- The difference between authentication (who you are) and authorization
  (what you're allowed to access).
- BOLA / IDOR: the #1 risk on the OWASP API Security Top 10.
- A vulnerability lifecycle: intentional flaw → exploitation → remediation.

## Tech Stack
Flask, Flask-Login (session auth), Flask-SQLAlchemy, SQLite, Werkzeug (scrypt password hashing), gunicorn (production WSGI server), deployed on Render over HTTPS.

## Setup
1. Create and activate a virtual environment:
   `python -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Set a secret key: create a `.env` file with `SECRET_KEY=<your-random-key>`
   (generate one with `python -c "import secrets; print(secrets.token_hex(32))"`)
4. Run locally: `python app.py` (or `gunicorn app:app` for production-style)

## The Vulnerability
The GET, PATCH, and DELETE handlers on `/notes/<id>` are all authenticated using `@login_required`, but none of them check ownership (authorization). That gap is the vulnerability: the application confirms the current user is logged in, but never verifies that the note they're accessing actually belongs to them. 


## Exploitation Walkthrough
`@login_required` correctly enforces authentication, but the vulnerable routes
never check whether the current user *owns* the note they're requesting. An
authenticated attacker can read, modify, or delete any user's notes by changing
the ID in the URL.

Full walkthrough with request/response evidence (read, enumerate, modify,
delete, and a control test) is in the writeup: [Access Control / IDOR writeup](/Writeups/access-control-idor.md)

## Remediation
Ownership is enforced through a single helper function, called at the start of
each affected route. It fetches the note and confirms it belongs to the current
user before the route acts on it, so the authorization check lives in one place
rather than being duplicated across handlers.

Full remediation details, including the deliberate choice to return 404 rather
than 403, are in the [writeup](/Writeups/access-control-idor.md).

## Vulnerable vs Fixed
The `main` branch holds the remediated code. The deliberately vulnerable
version is preserved at the `vulnerable-version` git tag:
`git checkout vulnerable-version` to inspect the original flaw.

## License
MIT — see LICENSE.