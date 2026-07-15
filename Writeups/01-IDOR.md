# Broken Object Level Authorization (IDOR) in a Multi-User Notes API

## Summary

A Flask-based multi-user notes API I built and deployed to a live public host exposed a Broken Object Level Authorization flaw (IDOR) on its per-note endpoints. Any authenticated user could read, modify, or delete any other user's notes simply by changing the numeric note ID in the request path. Severity is high: a single missing ownership check broke confidentiality, integrity, and availability across every user's data.

## Affected Endpoints

Base host: `https://flask-bola-lab.onrender.com`

Three routes were vulnerable, all operating on a client-supplied note ID:

- `GET /notes/<id>`
- `PATCH /notes/<id>`
- `DELETE /notes/<id>`

All three enforced `@login_required` but none verified that the requesting user actually owned the note. The API runs on a live Render deployment over HTTPS with session-based authentication via Flask-Login.

One endpoint was never affected: `GET /notes/mine`. It scoped its query by `owner_id`, so it only ever returned the caller's own notes. That contrast matters, and the Root Cause section explains why.

## Root Cause Analysis

The vulnerable controllers looked up the note by primary key and trusted the ID the client sent. Nothing compared the note's owner against the logged-in user before acting on it.

The distinction the code missed is the one between authentication and authorization. Authentication answers "who are you," and `@login_required` handled that correctly. Authorization answers "are you allowed to touch this specific object," and that check was simply absent. The app confirmed you were logged in, then handed you whatever note ID you asked for.

`GET /notes/mine` is the tell. Same app, same session handling, but it scoped its query by `owner_id` and was never exploitable. The vulnerable routes did a naive lookup by ID alone. The flaw was not the framework or the auth layer. It was the by-ID lookup that trusted user input to name an object without checking ownership of that object.

Sequential integer IDs made the situation worse. An attacker does not need to discover a target ID in advance. They start at 1 and count.

This maps to CWE-639 and OWASP API1:2023 Broken Object Level Authorization.

## Exploitation

All requests were sent through Burp Repeater using a legitimately authenticated attacker session against the live host. The attacker held a valid, ordinary account. No credentials were stolen and no authentication was bypassed. The attacker just requested objects that were not theirs.

**Read another user's note.** A `GET` for a victim's note ID returned `200 OK` with the victim's confidential content.

![Vulnerable Application's GET request from attacker giving 200](/Screenshots/Vuln/vuln_GET_200.png)

**Enumerate across users.** Incrementing the ID walked through other users' notes; some IDs returned another user's data (200), others returned 404 for empty slots. Both confirm the attacker can probe the full range.

![Vulnerable Application's Enumeration attempt from attacker giving 200](/Screenshots/Vuln/vuln_enum_GET_200.png)

![Vulnerable Application's Enumeration attempt from attacker giving 404](/Screenshots/Vuln/vuln_enum_GET_II_404.png)

**Modify another user's note.** A `PATCH` carrying an altered body, aimed at a victim's note ID, was accepted. The victim's content was overwritten with the attacker's.

![Vulnerable Application's PATCH req from attacker giving 200](/Screenshots/Vuln/vuln_PATCH_200.png)

**Delete another user's note.** A `DELETE` against a victim's note ID destroyed it.

![Vulnerable Application's DELETE req from attacker giving 200](/Screenshots/Vuln/vuln_DELETE_200.png)

**Control test.** The same request replayed with no session cookie returned `401 Unauthorized`. This proves authentication was enforced and isolates the finding to authorization rather than an auth bypass. The endpoint was not open. It was open to the wrong authenticated users.

![Vulnerable Application's GET req from attacker with no session key giving 401](/Screenshots/Vuln/vuln_control_test_401.png)

## Impact

One missing check compromised all three security properties:

- **Confidentiality.** `GET` exposed any user's private notes.
- **Integrity.** `PATCH` let an attacker rewrite any user's notes.
- **Availability.** `DELETE` let an attacker destroy any user's notes.

Sequential integer IDs turn a targeted attack into bulk harvesting. Because the attacker can enumerate the full ID range, they do not need to know in advance which notes exist or who owns them. They can iterate the entire object space and touch every note in the system. For an application holding private user data, that is a full breach of the data set from a single low-privileged account.

## Remediation

The fix centralizes object-level authorization in one helper, `get_owned_note_or_error(note_id)`. It fetches the note, returns `404` if the note does not exist, and returns `404` if the note's owner does not match the current user. Every route calls it before touching the note. All three vulnerable routes were refactored to use it. `GET /notes/mine` needed no change, since it was already scoped by owner.

Two decisions are worth calling out.

**Return 404, not 403, for unauthorized access.** A `403 Forbidden` confirms the object exists but is off limits, which leaks existence to an attacker enumerating IDs. Returning `404` for both "does not exist" and "not yours" makes those two cases indistinguishable. The attacker learns nothing about the object space by walking the range. This is a deliberate enumeration-hardening choice, not an accident of routing.

**Enforce authorization in one place, not inline per route.** Duplicating the ownership check across three handlers invites drift, where one route gets patched and another quietly does not. A single mandatory helper means there is one place to get right and one place to audit.

After the fix, the attacker's identical requests return `404`, while the legitimate owner still receives `200` for their own note. The fix closes unauthorized access without breaking legitimate access.

![Fixed Application's GET req from attacker giving 404](/Screenshots/Fixed/fixed_attacker_req_404.png)

![Fixed Application's GET req from owner(victim) giving 200](/Screenshots/Fixed/fixed_owner_req_200.png)

## Key Takeaway

Authentication is not authorization. Confirming that a request comes from a logged-in user says nothing about whether that user may act on the specific object they named. Any route that loads an object by a client-supplied identifier needs an ownership check, and that check belongs in one shared, mandatory place rather than copied across handlers. When identifiers are sequential, pair it with a return-404-not-403 habit so the application does not narrate its object space to anyone counting through the IDs.
