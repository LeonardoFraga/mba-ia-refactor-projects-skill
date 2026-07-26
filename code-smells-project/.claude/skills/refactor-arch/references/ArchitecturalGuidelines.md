# Architectural Guidelines — Target MVC (Phase 3)

Rules for the MVC architecture the refactor must produce. Applies to
Python/Flask, Node/Express and other backends — map the concepts to the
framework's idioms.

## Layers and responsibilities

- **Models** — data access, schema, pure domain rules. Expose `find`, `create`,
  `update`, `delete`. **Never** touch `request`/`req`/`res` or build HTTP
  responses. Independent of routing.
- **Controllers** — the bridge between routes and models/services. Validate and
  sanitize input, orchestrate the flow, handle domain errors, return plain
  serializable data (dict / DTO). Testable without the HTTP framework.
- **Views / Routes** — declare endpoints, methods and path params; map
  request/query/body to controller calls; translate the controller's return into
  an HTTP response (status + JSON). Thin — no business logic, no SQL.
- **Middlewares** — cross-cutting concerns: centralized error handling,
  validation, CORS, auth. Reusable, business-agnostic.
- **Config** — settings, connection strings and secrets from environment
  variables. Nothing hardcoded in source.
- **Composition root** — the entry point (`app.py` / `app.js`) only wires
  dependencies and starts the server.

## Suggested layout

```
src/
├── config/         # settings.py / config.js — env + secrets
├── models/         # <domain>_model per domain
├── controllers/    # <domain>_controller per domain
├── views/ (routes) # route declarations
├── middlewares/    # error_handler, validation
└── app entry       # composition root
```

## Dependency direction (one-way)

- Python/Flask: `routes` → `controllers` → `models`. `models` never import
  `routes`/`controllers`.
- Node/Express: `routes/*.js` → `controllers/*.js` → `models/*.js`. `models`
  never import routes or the HTTP app.

## Design principles

- **Dependency Injection** — pass repositories, clients and config into
  functions/constructors instead of importing concrete singletons.
- **Single Responsibility** — one reason to change per file/function.
- **Separation of Concerns** — validation, persistence, routing, presentation
  live in distinct layers.
- **Parameterized queries only** — no string-built SQL anywhere.

## Post-refactor validation checklist

- [ ] Original endpoints keep the same paths + methods + response shape.
- [ ] No SQL/NoSQL queries inside route definitions.
- [ ] No `request`/`req`/`res` inside models.
- [ ] No secrets in source (all via `config/` + env).
- [ ] Error handling is centralized (middleware / error handler).
- [ ] The app boots and endpoints respond.

## Adapting to already-organized projects

If the project already has `models/`, `routes/`, `services/`: keep what is
correct, and fix the leaks — move business/serialization logic out of routes into
controllers/services, extract config, replace insecure crypto, remove duplication
and N+1 queries. Do not rebuild from scratch when a clean seam already exists.
