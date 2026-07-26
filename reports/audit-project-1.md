================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project (API da Loja)
Stack:   Python 3 + Flask 3.1.1 (flask-cors 5.0.1) + SQLite
Files:   4 source files analyzed | ~780 lines of code

Summary
CRITICAL: 6 | HIGH: 3 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] God File — models.py mixes 4 domains + data access + business rules
File: models.py:1-314
Description: A single module holds data access and business logic for produtos
(lines 4-70, 285-314), usuarios (72-131), pedidos (133-233, 275-283) and
relatorios/vendas (235-273). It concentrates SQL, domain calculations (discount
tiers 256-262, ticket médio 272) and serialization in one place.
Impact: Impossible to test a domain in isolation; every change ripples across
unrelated concerns; the file is the single point of failure for the whole app.
Recommendation: Split by domain into models/produto_model.py, usuario_model.py,
pedido_model.py, and move discount/report calculations into a controller/service.

[CRITICAL] Hardcoded Secrets & Config
File: app.py:7-8 (SECRET_KEY, DEBUG), app.py:88 (debug=True)
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` and
`app.config["DEBUG"] = True` are literal source values; `app.run(..., debug=True)`
hardcodes debug mode. The same secret is duplicated at controllers.py:289.
Impact: Credential leak committed to VCS; the app cannot be configured per
environment; debug mode exposes the interactive Werkzeug console in production.
Recommendation: Move SECRET_KEY / DEBUG / DB_PATH to config/settings.py read from
os.getenv, with no secret literal in source.

[CRITICAL] SQL Injection via String Concatenation (pervasive)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151,
155-166, 174, 188, 192, 206, 220, 224, 279-281, 289-297
Description: Nearly every query is built by concatenating user input directly
into SQL, e.g. get_produto_por_id (`"... WHERE id = " + str(id)`, line 28),
login_usuario (`"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`,
lines 109-111), criar_produto (47-50), criar_usuario (126-129), buscar_produtos
LIKE clauses (289-297), and every pedido INSERT/UPDATE (148-166, 279-281).
Impact: Full database compromise — authentication bypass on /login, arbitrary
read/write/delete on all tables. This is the single most dangerous class of bug
in the codebase.
Recommendation: Replace every query with parameterized statements
(`cursor.execute("... WHERE id = ?", (id,))`); build dynamic filters with a
params list, never with string concatenation.

[CRITICAL] Arbitrary SQL Execution & Unauthenticated Destructive Admin Endpoints
File: app.py:59-78 (/admin/query), app.py:47-57 (/admin/reset-db)
Description: `/admin/query` reads `dados.get("sql")` from the request body and
executes it verbatim (line 69), returning rows or committing writes — a remote
arbitrary-SQL primitive with no authentication. `/admin/reset-db` deletes every
row of all four tables (lines 51-54) with no auth guard.
Impact: Any unauthenticated caller can read, alter or destroy the entire
database. Catastrophic data loss / total compromise.
Recommendation: Remove /admin/query entirely. Keep /admin/reset-db only as a
fixed-statement operation, ideally behind an auth guard.

[CRITICAL] Plaintext Passwords & Weak Credential Handling
File: database.py:75-83 (seed), models.py:126-129 (insert), models.py:84
& models.py:99 (senha returned in serialization)
Description: Passwords are stored in cleartext (seed users at database.py:76-78:
"admin123", "123456"; criar_usuario inserts the raw senha). Worse, the password
is echoed back to clients: get_todos_usuarios (models.py:84) and
get_usuario_por_id (models.py:99) include `"senha": row["senha"]`, exposed via
GET /usuarios and GET /usuarios/<id>.
Impact: Total credential exposure — every user's password is readable via a
public endpoint and trivially recovered on any DB leak.
Recommendation: Hash passwords with werkzeug.security.generate_password_hash;
verify with check_password_hash; NEVER include the password/hash field in any
serialized response (behavior change — noted).

[CRITICAL] Sensitive Configuration Exposure via /health
File: controllers.py:287-289
Description: GET /health returns `"db_path": "loja.db"`, `"debug": True` and
`"secret_key": "minha-chave-super-secreta-123"` in its JSON body.
Impact: The application secret and internal config are handed to any
unauthenticated caller — enabling session forgery and reconnaissance.
Recommendation: /health must return only liveness/DB status and counts; never
leak secrets or config. Remove the secret_key/debug/db_path fields.

[HIGH] Shared Mutable Global State — global db_connection
File: database.py:4, 8-11
Description: A module-level mutable `db_connection` is lazily assigned inside
get_db via `global db_connection` and shared across all requests with
check_same_thread=False.
Impact: Race conditions and non-deterministic behavior under concurrency; the
single shared connection/cursor state is hard to reason about and test.
Recommendation: Provide a connection factory (per-request connection or a
properly encapsulated pool) in config/database.py; stop mutating module globals.

[HIGH] Business Logic & Side Effects in Controllers
File: controllers.py:208-210 (email/SMS/push on order), controllers.py:248-250
(status-change notifications), controllers.py:266-274 (health hits DB directly)
Description: Controllers embed notification side effects as print statements
(ENVIANDO EMAIL/SMS/PUSH), branch on domain status, and health_check runs its own
SQL against get_db bypassing the model layer.
Impact: Notification and persistence concerns are untestable and non-reusable,
tangled into HTTP handlers; violates separation of concerns.
Recommendation: Move notification into a dedicated service/helper invoked by the
controller; route health DB access through a model function.

[HIGH] Tight Coupling Between Layers (no separation / DI)
File: controllers.py:3 & 266 (controller imports get_db), app.py:49 & 66
(routes import get_db and run SQL inline)
Description: The route file (app.py) opens DB cursors and executes SQL directly in
/admin handlers; the controller imports the DB driver and queries it in
health_check — layers reach past their neighbors instead of routes→controllers→
models.
Impact: Layers cannot be swapped, mocked or tested independently; the dependency
direction is violated.
Recommendation: Enforce one-way flow routes → controllers → models; only models
touch the DB.

[MEDIUM] N+1 Queries When Building Orders
File: models.py:187-193 (get_pedidos_usuario), models.py:219-225 (get_todos_pedidos)
Description: For each pedido a query fetches its itens, then for each item a
further query fetches the produto nome — one query per item per order inside
nested loops.
Impact: Query count grows linearly with orders×items; performance collapses as
data grows.
Recommendation: Replace with a single JOIN across pedidos/itens_pedido/produtos
(parameterized) and group rows in memory.

[MEDIUM] Duplicate Logic / Duplicate Serialization
File: models.py:171-201 vs 203-233 (near-identical pedido builders);
models.py:12-21, 31-40, 304-313 (produto dict copy-pasted 3×)
Description: get_pedidos_usuario and get_todos_pedidos are almost identical apart
from the WHERE clause; the produto serialization dict is duplicated across three
functions.
Impact: Costly maintenance and drift — a field change must be made in several
places.
Recommendation: Extract a shared serialize_pedido / serialize_produto helper and
a single order-fetch function parameterized by an optional usuario_id.

[MEDIUM] Missing / Weak Input Validation
File: controllers.py:146-165 (criar_usuario: no email format or length checks),
controllers.py:188-203 (criar_pedido: item shape/quantidade not validated),
controllers.py:118-121 (buscar_produtos: float() cast unguarded), 167-186 (login)
Description: criar_usuario accepts any email string and no password policy;
criar_pedido does not validate that each item has produto_id/quantidade of the
right type; buscar_produtos casts query params to float without a try/guard
(raises 500 on bad input).
Impact: Silent data corruption, 500 errors, inconsistent persisted data.
Recommendation: Validate presence, type, format and range in the controller
before delegating; return 400 on invalid input.

[LOW] Deprecated / Unsafe Runtime Practice — debug=True in production path
File: app.py:8, app.py:88
Description: Debug mode is hardcoded on (`app.config["DEBUG"] = True` and
`app.run(debug=True)`); the app self-describes as `"ambiente": "producao"`
(controllers.py:286).
Impact: Enables the interactive debugger/reloader in production — an RCE vector
and unsupported for real deployments.
Recommendation: Drive debug from an environment variable defaulting to false.

[LOW] Debug Print Noise & Raw Exception Leakage in Handlers
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248-250;
app.py:56 — plus inline dict serialization scattered in models
Description: Numerous print(...) debug statements act as pseudo-logging and side
effects inside handlers; raw exception strings are returned to clients
(`jsonify({"erro": str(e)})`) leaking internals.
Impact: Lower readability/maintainability; error detail leakage; no real logging.
Recommendation: Replace prints with the logging module; centralize error handling
in a middleware that returns safe messages.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
