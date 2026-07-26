================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 (Flask-CORS 4.0.0)
Dependencies:  flask==3.0.0, flask-sqlalchemy==3.1.1, flask-cors==4.0.0, marshmallow==3.20.1, requests==2.31.0, python-dotenv==1.0.0
Domain:        Task Manager API — entities: User, Task, Category (auth + reports)
Architecture:  Partially separated — has models/, routes/, services/, utils/, but responsibilities leak: business + serialization logic lives inside routes (fat blueprints), secrets are hardcoded in app.py, models expose the password hash, overdue logic is duplicated in 6 places, and N+1 queries appear in routes/reports.
Source files:  15 Python files analyzed (~1158 LOC incl. seed)
DB tables:     users, tasks, categories (SQLite tasks.db)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3 + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1158 lines of code

Summary
CRITICAL: 4 | HIGH: 1 | MEDIUM: 4 | LOW: 3

Findings

[CRITICAL] Hardcoded secrets / configuration in source
File: app.py:11-13
Description: SECRET_KEY = 'super-secret-key-123' and the SQLALCHEMY_DATABASE_URI 'sqlite:///tasks.db' are hardcoded literals in the composition root, committed to source control.
Impact: Credential leak; the app cannot be reconfigured per environment (dev/staging/prod) without editing code; a leaked repo leaks the signing key.
Recommendation: Move SECRET_KEY and the DB URI to config/settings.py reading from os.getenv / python-dotenv (.env), with dev-only fallbacks. Never commit real secrets.

[CRITICAL] Weak / broken cryptography for passwords (MD5)
File: models/user.py:29 (set_password), models/user.py:32 (check_password); import hashlib at line 3
Description: Passwords are hashed with unsalted hashlib.md5(pwd.encode()).hexdigest(). MD5 is cryptographically broken and unsalted, so identical passwords produce identical digests and are trivially reversed with rainbow tables.
Impact: On any DB breach, user credentials are recovered almost instantly. Fails every modern password-storage standard.
Recommendation: Replace MD5 with werkzeug.security.generate_password_hash / check_password_hash (PBKDF2/scrypt, salted). Migrate seed passwords to the new scheme.

[CRITICAL] Password hash exposed in serialization and API responses
File: models/user.py:21 (to_dict includes 'password'); echoed by routes/user_routes.py:85-86 (create_user), routes/user_routes.py:33 (get_user), routes/user_routes.py:209 (login returns user.to_dict())
Description: User.to_dict() includes the 'password' field, and every endpoint that serializes a user (create, get-by-id, login) returns the stored password hash to the client.
Impact: Leaks the credential material over the wire to any caller; combined with MD5 this hands attackers the hash to crack offline. Sensitive-data exposure.
Recommendation: Remove 'password' from User.to_dict() entirely. Login and user endpoints then naturally stop leaking it. (Behavior change — documented; seed/login still work against the hashed value internally.)

[CRITICAL] Hardcoded SMTP credentials
File: services/notification_service.py:7-10
Description: The email host, port, user 'taskmanager@gmail.com' and password 'senha123' are hardcoded in NotificationService.__init__.
Impact: SMTP account credentials leak with the source; cannot rotate or differ per environment.
Recommendation: Load host/port/user/password from config/settings.py via os.getenv. Keep the service class but inject the config.

[HIGH] Fat routes — business & serialization logic inside blueprints
File: routes/task_routes.py:12-63 (get_tasks hand-builds dicts + recomputes overdue + fetches user/category), routes/task_routes.py:273-303 (task_stats), routes/report_routes.py:13-101 (summary_report), routes/report_routes.py:103-155 (user_report)
Description: Route handlers parse input, run queries, compute derived values (overdue, completion_rate, per-user aggregates) and hand-assemble response dicts field-by-field, with no controller/service delegation. get_tasks duplicates the model's to_dict logic manually.
Impact: Logic cannot be reused or unit-tested without the HTTP layer; control flow is tangled; every response shape change means editing routing code. Destroys separation of concerns.
Recommendation: Introduce controllers/ (task_controller, user_controller, report_controller, category_controller) that return plain data; make routes thin (request -> controller -> jsonify). Centralize serialization in model to_dict().

[MEDIUM] N+1 queries / query in a loop
File: routes/task_routes.py:42 (User.query.get per task) & routes/task_routes.py:51 (Category.query.get per task); routes/report_routes.py:56 (Task.query.filter_by(user_id=...) per user); routes/report_routes.py:163 (Task.query.filter_by(category_id=...).count() per category)
Description: get_tasks issues one user query and one category query for every task in the loop. summary_report queries tasks once per user; get_categories counts tasks once per category.
Impact: Query count grows linearly with rows; performance collapses as data grows. 10 tasks already means ~21 queries in get_tasks alone.
Recommendation: Use eager loading (joinedload(Task.user), joinedload(Task.category)) or batch the lookups (single IN query grouped in memory). For reports, aggregate with group_by counts.

[MEDIUM] Duplicated overdue / date logic
File: models/task.py:50-60 (is_overdue) vs routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-287, routes/user_routes.py:171-180, routes/report_routes.py:34-37, routes/report_routes.py:132-135
Description: The exact overdue rule (due_date < now AND status not in done/cancelled) is re-implemented inline in 6 different places instead of reusing Task.is_overdue().
Impact: High maintenance cost; the rule will diverge over time (one place could be fixed and others missed).
Recommendation: Keep ONE implementation in Task.is_overdue() (fixed to timezone-aware now) and call it everywhere; expose overdue via to_dict() options where routes need it.

[MEDIUM] Bare except swallowing errors
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:204, routes/task_routes.py:236; routes/user_routes.py:130, routes/user_routes.py:149; routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221; utils/helpers.py:46, utils/helpers.py:49, utils/helpers.py:88
Description: Bare `except:` blocks catch everything (including KeyboardInterrupt/SystemExit) and return a generic 500 or None, hiding the real error and its stack trace.
Impact: Debugging is nearly impossible; real bugs are masked as generic failures; unexpected control-flow interruptions are swallowed.
Recommendation: Catch specific exceptions (ValueError for parsing, SQLAlchemyError for DB) and route unexpected errors to centralized error handling (middlewares/error_handler.py).

[MEDIUM] Missing / weak input validation and no centralized error handling
File: routes/task_routes.py:261 & 264 (int(priority)/int(user_id) on unguarded query params), routes/report_routes.py:196-202 (update_category reads request.get_json() without a None guard), app.py (no error handlers registered)
Description: Query params are cast to int without try/guard (a non-numeric ?priority=x raises 500); update_category assumes a JSON body; there is no application-level error handler, so uncaught errors surface as raw stack traces.
Impact: Invalid input produces 500s instead of clean 400s; inconsistent error responses across endpoints.
Recommendation: Guard casts, validate presence/type, and register a centralized error handler (400/404/500 -> JSON) via a middleware module.

[LOW] Deprecated / obsolete API usage  (mandatory check)
File: datetime.utcnow() at models/user.py:14, models/task.py:15-16,52, routes/task_routes.py:31,285, routes/user_routes.py:172, routes/report_routes.py:35,42,45,71,133, services/notification_service.py:35, utils/helpers.py:38, seed.py:66-75 (18 occurrences); legacy Query.get() at routes/task_routes.py:42,51,67,117,122,158,188,195,227; routes/user_routes.py:29,94,136,155; routes/report_routes.py:105,192,213 (16 occurrences)
Description: datetime.utcnow() is deprecated in Python 3.12+; the legacy SQLAlchemy Query.get() pattern is superseded by Session.get().
Impact: Emits deprecation warnings and will break on future upgrades; utcnow() returns a naive datetime that invites timezone bugs.
Recommendation: Use datetime.now(timezone.utc) and db.session.get(Model, id) where practical.

[LOW] Unused imports scattered across modules
File: app.py:7 (os, sys, json), routes/task_routes.py:7 (json, os, sys, time), routes/user_routes.py:6 (hashlib, json — hashlib no longer needed), routes/report_routes.py:8 (json), utils/helpers.py:3-7 (os, json, sys, math, hashlib)
Description: Several modules import modules they never use (leftover from earlier code).
Impact: Noise; misleads readers about dependencies; slows comprehension.
Recommendation: Remove all unused imports.

[LOW] Debug print() leftovers and magic numbers in handlers
File: routes/task_routes.py:149,153,219,234 (print), routes/user_routes.py:83,89,147 (print); magic numbers priority 1..5 / title length 3..200 repeated inline in routes
Description: print() debug statements are left inside request handlers, and validation magic numbers are duplicated inline instead of referencing the constants already defined in utils/helpers.py.
Impact: Log noise in production; magic numbers duplicated (utils/helpers.py already defines MAX_TITLE_LENGTH etc.).
Recommendation: Remove debug prints (or use logging); reference the shared constants for validation bounds.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

> (This run carries prior human approval — answered `y`. Proceeding to Phase 3.)
