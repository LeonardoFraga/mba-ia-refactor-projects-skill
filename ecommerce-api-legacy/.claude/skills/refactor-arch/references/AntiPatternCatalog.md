# Anti-Pattern Catalog — Phase 2

Detection signals, impact and severity for the anti-patterns this skill hunts.
For each match, emit a finding with `file:line(s)`, description, impact and a
recommendation, then order findings CRITICAL → HIGH → MEDIUM → LOW.

## Severity scale

- **CRITICAL** — security holes or architecture failures that break the app,
  expose data, or fully destroy separation of concerns.
- **HIGH** — strong MVC/SOLID violations that badly hurt maintainability and
  testability (heavy business logic in controllers, tight coupling, mutable
  global state).
- **MEDIUM** — duplication, moderate performance issues (N+1), missing route
  validation, misused middleware.
- **LOW** — readability, naming, magic numbers, minor standardization.

---

## 1. God Class / God File — CRITICAL
Signals: a single file holds routes + business logic + data access + validation;
functions > 80–100 lines with many responsibilities; one `models.py` /
`AppManager.js` serving several domains.
Impact: impossible to test in isolation; any change ripples everywhere.

## 2. Hardcoded Secrets / Config — CRITICAL
Signals: literals like `SECRET_KEY`, `DB_PASSWORD`, `API_KEY`, `paymentGatewayKey`,
`pk_live_...`, SMTP passwords, hardcoded `SECRET_KEY = '...'` in source.
Impact: credential leak; app cannot be configured per environment.

## 3. SQL Injection via String Concatenation — CRITICAL
Signals: queries built with `+`, f-strings or template literals from user input:
`"SELECT * FROM produtos WHERE id = " + str(id)`,
`` `... WHERE email = '${req.body.email}'` ``. `request.args`/`req.body`/`params`
flowing straight into a SQL string.
Impact: full database compromise. Fix with parameterized queries.

## 4. Arbitrary/Raw Query Execution & Dangerous Admin Endpoints — CRITICAL
Signals: an endpoint that executes a SQL string taken from the request
(`/admin/query` running `dados.get("sql")`); destructive endpoints with no
auth (`/admin/reset-db`, unauthenticated `DELETE`).
Impact: remote code/DB execution; catastrophic data loss.

## 5. Weak / Broken Cryptography for Passwords — CRITICAL
Signals: passwords stored in plaintext; `hashlib.md5(...)` or a homemade
`badCrypto()` for password hashing; passwords echoed back in API responses /
`to_dict()`.
Impact: credentials trivially recovered on breach. Use bcrypt/argon2/scrypt.

## 6. Fat Controller / Business Logic in Routes — HIGH
Signals: a route parses payload, validates, queries the DB, computes and formats
the response with no service/model delegation; `@app.route`/`app.post(...)` with
loops, branches and inline SQL; nested DB callbacks inside a handler.
Impact: no reuse, no isolated testing, tangled control flow.

## 7. Tight Coupling Between Layers (no Dependency Injection) — HIGH
Signals: controllers instantiate concrete DB drivers directly; models import
`request`/`req`/`res`/`session`; routes import DB drivers instead of controllers;
a class that both owns the DB connection and defines routes.
Impact: layers cannot be swapped, mocked, or tested independently.

## 8. Shared Mutable Global State — HIGH
Signals: module-level mutable globals updated by many handlers
(`globalCache = {}`, `totalRevenue = 0`, a global `db_connection`); singletons
exported as `cache`/`state` without encapsulation.
Impact: race conditions, non-deterministic behavior, hard debugging.

## 9. N+1 Queries / Query in a Loop — MEDIUM
Signals: a `for` loop issuing one query per iteration
(`for row in rows: cursor.execute("SELECT ... WHERE id = " + id)`);
per-item lookups inside `.forEach`/list comprehensions; building a report by
querying each child row separately.
Impact: performance collapses as data grows. Use JOINs / batched queries.

## 10. Missing Input Validation in Routes — MEDIUM
Signals: routes consuming `request.json`/`req.body` fields without checking
presence/type; casting query params (`int(...)`) without guarding; no length or
range checks before persistence.
Impact: silent errors, 500s, inconsistent data.

## 11. Duplicate Logic / Duplicate Queries — MEDIUM
Signals: the same serialization block or SQL snippet copy-pasted across handlers
(e.g. two functions building the identical `pedido` dict with nested item
queries); repeated overdue/date logic in several routes.
Impact: costly maintenance, divergence over time.

## 12. Deprecated / Obsolete API Usage — MEDIUM  *(mandatory check)*
Signals:
- **Express/Node:** `body-parser` (`bodyParser.json()`) instead of
  `express.json()`; `req.param(...)`; `app.configure`; old `sqlite3` verbose
  callback API where a modern promise driver fits; `new Buffer(...)`.
- **Flask/Python:** `flask.ext.*` imports; `Flask.run(debug=True)` in production;
  `datetime.utcnow()` (deprecated in 3.12+, prefer `datetime.now(timezone.utc)`);
  `Query.get()` legacy SQLAlchemy 1.x style where `db.session.get()` is preferred;
  `hashlib.md5` for security.
Impact: breaks on upgrades; unsupported, unsafe practices. Recommend the modern
equivalent.

## 13. Presentation/Serialization Logic in the API Layer — LOW
Signals: routes hand-building JSON dicts field-by-field and formatting inline
instead of delegating to a model `to_dict()`/serializer; HTTP status, error text
and payload all mingled in one block.
Impact: readability suffers; serialization must be extracted later.

## 14. Poor Naming / Magic Numbers / Debug Leftovers — LOW
Signals: single-letter vars (`u`, `e`, `p`, `cc`); magic numbers
(`priority > 5`, `10000` loop count); `print(...)`/`console.log` debug noise in
handlers; `debug=True` hardcoded; bare `except:` swallowing errors.
Impact: lower readability and maintainability.

---

## How to use
1. Grep each source file for the signals above.
2. Classify by severity; record `file:line(s)`, description, impact, recommendation.
3. Always run check #12 (deprecated APIs) explicitly.
4. Feed each finding to `RefactoringPlaybook.md` for the transformation.
