================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js) — CommonJS, v24.x runtime
Framework:     Express ^4.18.2
Dependencies:  express ^4.18.2, sqlite3 ^5.1.6
Domain:        LMS / e-commerce checkout (entities: users, courses, enrollments, payments, audit_logs)
Architecture:  Monolithic — a single God class (AppManager.js) owns the DB connection, defines every route and holds all business logic; utils.js holds secrets + global mutable state
Source files:  3 files analyzed (src/app.js, src/AppManager.js, src/utils.js) | ~180 LOC
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy (Frankenstein LMS)
Stack:   JavaScript / Node.js + Express ^4.18.2 (SQLite in-memory via sqlite3 ^5.1.6)
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] Hardcoded secrets and credentials in source
File: src/utils.js:1-7 (dbPass:3, paymentGatewayKey:4, smtpUser:5)
Description: Production database password ('senha_super_secreta_prod_123'), live payment gateway key ('pk_live_1234567890abcdef') and SMTP user are literal string values committed in the config object.
Impact: Any repository reader gains live payment and DB credentials; the app cannot be configured per environment; secrets leak into version control history.
Recommendation: Move every secret to environment variables read in config/settings.js (process.env.PAYMENT_GATEWAY_KEY, DB_USER, DB_PASS, SMTP_USER). Never commit real keys; provide a .env.example instead.

[CRITICAL] God class — AppManager owns DB connection, all routes and all business logic
File: src/AppManager.js:4-141 (constructor:5-8, initDb:10-23, setupRoutes:25-138)
Description: A single class opens the sqlite connection (this.db), builds the schema, seeds data, and declares all three endpoints with inline validation, payment, enrollment, auditing and caching logic.
Impact: Nothing can be unit-tested in isolation; every change to any endpoint risks the whole app; total loss of separation of concerns.
Recommendation: Split by domain into config/ (db + settings), models/, services/, controllers/, routes/, middlewares/. AppManager disappears; app.js becomes a thin composition root.

[CRITICAL] Weak / broken cryptography for password hashing (badCrypto)
File: src/utils.js:17-23 (defined); src/AppManager.js:68 (used)
Description: Passwords are "hashed" by a homemade loop that base64-encodes the password and truncates to 10 chars — no salt, deterministic, trivially reversible. Seed data even stores the plaintext '123' (AppManager.js:18).
Impact: On any breach, all user credentials are recovered instantly; the scheme provides zero cryptographic protection.
Recommendation: Replace badCrypto with Node's built-in crypto.scrypt (salted) — implemented in services/cryptoService.js exposing hash()/verify(). Never store or echo plaintext passwords.

[CRITICAL] Sensitive data exposure — card number and gateway key logged to console
File: src/AppManager.js:45
Description: `console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)` writes the full PAN (credit card number) and the live gateway secret to stdout/logs on every checkout.
Impact: PCI-DSS violation; card numbers and the payment secret persist in log aggregators, exposing customers and enabling fraud.
Recommendation: Remove the log entirely. Never log PANs or secrets. If telemetry is needed, log only a masked last-4 and a correlation id inside the payment service.

[CRITICAL] Broken referential integrity on DELETE /api/users/:id (orphan records)
File: src/AppManager.js:131-137 (handler admits it at line 135)
Description: Deleting a user removes only the users row; enrollments and payments referencing that user are left behind. The response string literally states the rows "ficaram sujos no banco" (were left dirty in the DB).
Impact: Data corruption — orphaned enrollments/payments skew the financial report and break downstream integrity; the endpoint knowingly ships a broken state.
Recommendation: Wrap the delete in a transaction that cascades cleanup: delete payments for the user's enrollments, then the enrollments, then the user. Return a clean JSON confirmation.

[HIGH] Fat controller — POST /api/checkout does everything inline via nested DB callbacks
File: src/AppManager.js:28-78
Description: The route reads and validates the body, looks up the course, finds-or-creates the user, hashes the password, processes payment, inserts enrollment + payment + audit log and writes cache — all in one handler with 4 levels of nested sqlite callbacks.
Impact: No reuse, impossible to unit-test, tangled control flow and callback hell; error handling is scattered and inconsistent.
Recommendation: Extract into checkoutController (orchestration) + paymentService + models (userModel/courseModel/enrollmentModel/paymentModel) using a promisified db helper and async/await.

[HIGH] Tight coupling between layers — no dependency injection
File: src/AppManager.js:1-8 (this.db = new sqlite3.Database at :7), SQL in route bodies (37,40,50,54,57,83,92,104,106,133)
Description: The route layer instantiates the concrete sqlite3 driver directly and runs raw SQL inside handlers; there is no model/service seam to mock or swap.
Impact: Layers cannot be swapped, mocked or tested independently; switching DB drivers or adding caching forces edits across route code.
Recommendation: Centralize the connection in config/database.js and inject it into models; routes depend only on controllers; controllers depend only on services/models.

[HIGH] Shared mutable global state (globalCache, totalRevenue)
File: src/utils.js:9-10 (globalCache:9, totalRevenue:10); mutated via logAndCache src/utils.js:12-15, called at src/AppManager.js:59
Description: Module-level mutable globals are exported and mutated from handlers. totalRevenue is exported by value and never meaningfully updated (dead/broken state); globalCache is an unencapsulated shared map.
Impact: Race conditions under concurrency, non-deterministic behavior, and hard-to-debug shared state; the by-value export is a latent bug.
Recommendation: Encapsulate in services/cacheService.js (class with private store and get/set). Remove totalRevenue or compute revenue on demand from the DB.

[MEDIUM] N+1 query explosion in GET /api/admin/financial-report
File: src/AppManager.js:83-128 (courses.forEach:89 -> enrollments query:92 -> per-enrollment user query:104 + payment query:106)
Description: One query per course, then one query per enrollment, then two queries per student (user + payment). For C courses and N enrollments the handler fires roughly 1 + C + 2N queries, coordinated by fragile manual pending-counters.
Impact: Performance collapses as data grows; the hand-rolled counter logic is error-prone and can send the response early or never.
Recommendation: Replace with a single JOIN across courses / enrollments / users / payments, then group in memory in reportController — one query instead of N+1.

[MEDIUM] Missing / weak input validation on /api/checkout
File: src/AppManager.js:29-35
Description: Validation is only a truthy check on usr/eml/cid/cc (line 35). There is no email-format check, no type/range check on c_id, no card-format check, and pwd is silently defaulted to "123456" (line 68) when absent.
Impact: Malformed input reaches the DB and payment logic; silent weak-password defaults and inconsistent data.
Recommendation: Add a validation middleware that asserts presence, types, email format and card digits before the controller runs; reject with 400 + JSON error.

[MEDIUM] Deprecated / legacy API usage — sqlite3.verbose() callback driver
File: src/AppManager.js:1 (require('sqlite3').verbose()); callback style throughout (37,40,50,54,57,83,92,104,106,133)
Description: The legacy sqlite3 verbose callback API is used everywhere, forcing nested-callback control flow. verbose() is a debug mode not intended for production and the driver is effectively in maintenance.
Impact: Encourages callback hell, breaks on upgrades, and lacks first-class promise support.
Recommendation: Prefer a modern driver (better-sqlite3) or wrap the sqlite3 API in a promisified helper (util.promisify) so models can use async/await. This audit's refactor ships a promisified wrapper in config/database.js.

[LOW] Poor naming — single-letter variables in checkout
File: src/AppManager.js:29-33 (u, e, p, cid, cc)
Description: Request fields are bound to opaque single-letter names (u=user, e=email, p=password, cid=courseId, cc=card), obscuring intent.
Impact: Lower readability and maintainability; easy to confuse variables in the nested logic.
Recommendation: Use descriptive names (name, email, password, courseId, card) in the controller after validation.

[LOW] Presentation/serialization logic mingled into route handlers
File: src/AppManager.js:60, 112-115, 135
Description: Handlers hand-build response payloads and mix HTTP status, plaintext error strings ("Erro DB", "Curso não encontrado") and JSON inline, with no consistent envelope.
Impact: Inconsistent responses and status codes; serialization must be untangled later.
Recommendation: Have controllers return plain data and let thin routes serialize; centralize error-to-HTTP mapping in a middleware error handler.

================================
Total: 13 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
