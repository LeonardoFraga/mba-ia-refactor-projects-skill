# Project Analysis — Phase 1 Heuristics

Guides Phase 1: detect language, framework, database, domain, dependencies and
current architecture. Everything here is **evidence-based** — read files, do not
infer from the project's name.

## 1. Language detection

- File extensions: `.py` → Python · `.js/.mjs/.cjs` → JavaScript/Node ·
  `.ts` → TypeScript · `.rb` → Ruby · `.go` → Go · `.java` → Java.
- Manifest files: `requirements.txt` / `Pipfile` / `pyproject.toml` → Python ·
  `package.json` → Node · `go.mod` → Go · `Gemfile` → Ruby.
- Top-of-file signals: `import` / `from ... import` → Python ·
  `require(...)` / `import ... from` / `module.exports` → Node.

## 2. Framework + version detection

- **Flask (Python):** `from flask import`, `Flask(__name__)`, `@app.route`,
  `app.add_url_rule`, `flask_cors`, `Blueprint`. Version from `requirements.txt`
  (`flask==3.1.1`).
- **Django (Python):** `django.*`, `settings.py`, `urls.py`, `models.Model`.
- **FastAPI (Python):** `from fastapi import`, `APIRouter`, `@app.get`.
- **Express (Node):** `require('express')` / `import express`, `express()`,
  `app.use(...)`, `app.listen(...)`, `express.Router()`. Version from
  `package.json` dependencies.
- **Others:** `koa`, `hapi`, `nestjs`, `sails` — key on the import.

## 3. Database / persistence detection

- SQL drivers: `sqlite3`, `psycopg2`, `pymysql`, `sqlalchemy`, `pg`, `mysql2`,
  `knex`, `better-sqlite3`.
- NoSQL: `pymongo`, `mongoose`, `redis`, `cassandra`.
- Connection strings: `sqlite:///`, `postgres://`, `mysql://`, `mongodb://`,
  or a filename like `loja.db` / `tasks.db` passed to `sqlite3.connect`.
- **Table discovery:** grep for `CREATE TABLE`, `INSERT INTO`, `FROM <name>`,
  `UPDATE <name>` and list the distinct table names — report them.

## 4. Architecture mapping

- **Monolithic:** one (or a few) files hold init + routes + business logic + data
  access. Signal: SQL strings and `@app.route` in the same file, or a single
  `models.py` covering many domains.
- **Partially separated:** has some of `models/`, `routes/`, `services/`,
  `controllers/` — but responsibilities leak across layers (e.g. a service opens
  raw DB connections, a route runs queries).
- **Organized MVC:** entry point only wires the app; routes → controllers →
  models is a clean one-way dependency.

Record coupling smells: models importing `request`/`req`/`res`, routes importing
DB drivers directly, reciprocal imports.

## 5. Domain extraction

- From entity/table names, route paths, and log strings. Examples:
  - `produtos`, `usuarios`, `pedidos`, `itens_pedido` + `/relatorios/vendas`
    → **E-commerce API**.
  - `courses`, `enrollments`, `checkout`, `students` → **LMS / e-commerce checkout**.
  - `tasks`, `projects`, `users` + `/tasks` → **Task Manager API**.
- Answer for the summary: main domain? central entities? current architecture?

## 6. Metrics to collect

- Number of real source files and directories (exclude `node_modules`, `.venv`,
  `.git`, `__pycache__`, lockfiles).
- Approximate total lines of code.
- Detected dependencies from the manifest.

## Phase 1 output (see AuditReportTemplate.md for the exact block)

Report: Language · Framework (+version) · Dependencies · Domain · Architecture ·
Source files analyzed · DB tables.

## Phase 1 checklist

- [ ] Language detected correctly
- [ ] Framework (+ version) detected correctly
- [ ] Domain described correctly
- [ ] File count matches reality
- [ ] Dependencies and database identified
- [ ] Architecture classified (monolithic / partial / MVC)
