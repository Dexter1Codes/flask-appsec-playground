# Vulnerable Notes API — BOLA/IDOR Demonstration

A minimal multi-user Flask notes API built to demonstrate, exploit, and
remediate a Broken Object Level Authorization (BOLA / IDOR) vulnerability.

## ⚠️ Security Disclaimer
This application contains a **deliberate, documented vulnerability** for
educational purposes. It is intentionally insecure. Do **not** deploy it,
expose it to the internet, or run it with real data. For local learning only.

## What This Demonstrates
- The difference between authentication (who you are) and authorization
  (what you're allowed to access).
- BOLA / IDOR: the #1 risk on the OWASP API Security Top 10.
- A vulnerability lifecycle: intentional flaw → exploitation → remediation.

## Tech Stack
Flask, Flask-Login (session auth), Flask-SQLAlchemy, SQLite, Werkzeug (scrypt).

## Setup
(venv creation, pip install -r requirements.txt, SECRET_KEY in .env, how to run)

## The Vulnerability
(YOUR words: GET/PATCH/DELETE /notes/<id> are authenticated via @login_required
but never verify note ownership. Explain authn-vs-authz here.)

## Exploitation Walkthrough
(Register two users, log in as A, act on B's note by id, show the response.
Burp screenshots go here.)

## Remediation
(Added after the exploit: the ownership check, and why it closes all three routes.)

## License
MIT — see LICENSE.