# Refactoring Playbook — Phase 3

Concrete before/after transformations for the catalog anti-patterns, in
Python/Flask and Node/Express. Pick the one matching each finding.

## 1. God File → split by domain (Model / Controller / Route)
**Before**
```python
# app.py — routes + SQL + logic together
@app.route('/produtos')
def produtos():
    rows = db.execute('SELECT * FROM produtos').fetchall()
    return jsonify([dict(r) for r in rows])
```
**After**
```python
# models/produto_model.py
from config.database import get_db
def get_all():
    db = get_db()
    return [dict(r) for r in db.execute('SELECT * FROM produtos').fetchall()]

# controllers/produto_controller.py
from models import produto_model
def list_produtos():
    return produto_model.get_all()

# views/produto_routes.py
from flask import Blueprint, jsonify
from controllers import produto_controller
bp = Blueprint('produtos', __name__)
@bp.route('/produtos')
def produtos():
    return jsonify({"dados": produto_controller.list_produtos(), "sucesso": True})
```

## 2. Hardcoded Secrets → config + environment
**Before**
```python
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
```
**After**
```python
# config/settings.py
import os
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')
DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
DB_PATH = os.getenv('DB_PATH', 'loja.db')

# app.py
from config.settings import SECRET_KEY, DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
```
Node:
```js
// config/settings.js
module.exports = {
  port: process.env.PORT || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};
```

## 3. SQL Injection → parameterized queries
**Before**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**After**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```
Dynamic filters stay parameterized:
```python
query = "SELECT * FROM produtos WHERE 1=1"
params = []
if categoria:
    query += " AND categoria = ?"; params.append(categoria)
cursor.execute(query, params)
```

## 4. Dangerous raw-query / unauth admin endpoint → remove or guard
**Before**
```python
@app.route('/admin/query', methods=['POST'])
def executar_query():
    cursor.execute(request.get_json()['sql'])   # arbitrary SQL
```
**After**
```python
# Remove the arbitrary-SQL endpoint entirely. If an admin action is needed,
# expose a specific, parameterized operation behind authentication:
@bp.route('/admin/reset-db', methods=['POST'])
@require_admin
def reset_db():
    return admin_controller.reset_database()   # fixed statements, authorized
```

## 5. Weak crypto → strong password hashing, never return the hash
**Before**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
# to_dict() returns 'password': self.password
```
**After**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd):
    self.password = generate_password_hash(pwd)
def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
# to_dict() NEVER includes the password field
```
Node: replace `badCrypto()` with `bcrypt.hash(pwd, 10)` / `bcrypt.compare`.

## 6. Fat Controller / Business Logic in Route → Controller + Model
**Before**
```js
app.post('/api/checkout', (req, res) => {
  // reads body, queries DB, processes payment, inserts, formats — all inline
});
```
**After**
```js
// controllers/checkoutController.js
const checkoutModel = require('../models/checkoutModel');
async function checkout(req, res, next) {
  try {
    const result = await checkoutModel.process(req.body);
    res.status(201).json(result);
  } catch (e) { next(e); }
}
// routes/checkoutRoutes.js
router.post('/api/checkout', checkout);
```

## 7. Tight Coupling / God object → Dependency Injection
**Before**
```js
class AppManager {                     // owns DB AND defines routes
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  setupRoutes(app) { /* ... */ }
}
```
**After**
```js
// config/database.js exports a configured db instance
// models receive db via require; routes import controllers only
const db = require('../config/database');
module.exports = { findCourse: (id) => db.get('SELECT ...', [id]) };
```

## 8. Shared Mutable Global State → encapsulate
**Before**
```js
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```
**After**
```js
// services/cacheService.js
class CacheService {
  #store = {};
  set(k, v) { this.#store[k] = v; }
  get(k) { return this.#store[k]; }
}
module.exports = new CacheService();
```

## 9. N+1 Queries → single JOIN / batched query
**Before**
```python
for row in pedidos:
    itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row['id']))
    for item in itens:
        prod = db.execute("SELECT nome FROM produtos WHERE id = " + str(item['produto_id']))
```
**After**
```python
rows = db.execute("""
    SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome
    FROM itens_pedido ip JOIN produtos p ON p.id = ip.produto_id
    WHERE ip.pedido_id IN (%s)
""" % ",".join("?" * len(ids)), ids).fetchall()
# group in memory — one query instead of N+1
```

## 10. Missing Validation → validation middleware / helper
**Before**
```js
app.post('/tasks', async (req, res) => { await createTask(req.body); });
```
**After**
```js
// middlewares/validateTask.js
module.exports = (req, res, next) => {
  if (!req.body.title) return res.status(400).json({ error: 'title is required' });
  next();
};
router.post('/tasks', validateTask, taskController.create);
```

## 11. Deprecated API → modern equivalent
**Before**
```js
const bodyParser = require('body-parser');
app.use(bodyParser.json());
```
**After**
```js
app.use(express.json());
```
Flask:
```python
# Before: datetime.utcnow()  (deprecated)
from datetime import datetime, timezone
datetime.now(timezone.utc)
# Before: from flask.ext.cors import CORS
from flask_cors import CORS
```

## 12. Duplicate Logic → shared serializer/util
**Before**: two functions build the identical `pedido` dict with nested item queries.
**After**
```python
# models/pedido_model.py
def serialize_pedido(row, itens):
    return {"id": row["id"], "status": row["status"], "total": row["total"], "itens": itens}
# reused by get_pedidos_usuario and get_todos_pedidos
```

## 13. Presentation logic in route → controller returns data, route sends it
**Before**
```python
@app.route('/users')
def users():
    return jsonify([{'id': u['id'], 'name': u['name']} for u in get_users()])
```
**After**
```python
# controllers/user_controller.py returns plain data
def list_users(): return user_model.get_all()
# views/user_routes.py only serializes
@bp.route('/users')
def users(): return jsonify({"dados": user_controller.list_users()})
```

## 14. Composition root → centralize app wiring
**After**
```python
# app.py — composition root only
from flask import Flask
from config.settings import SECRET_KEY, DEBUG
from views import register_routes
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    register_routes(app)
    register_error_handlers(app)
    return app

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
```

## Workflow
1. Identify the anti-pattern and its `file:line`.
2. Apply the matching transformation.
3. Keep the public endpoint contract unchanged.
4. Validate: boot the app + hit the endpoints.
