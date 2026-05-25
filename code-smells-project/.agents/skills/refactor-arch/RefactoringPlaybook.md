# RefactoringPlaybook

Este playbook descreve transformações concretas para os anti-patterns do catálogo, com exemplos de antes/depois em Python/Flask e Node.js/Express.

## 1. God Class / God File → Extração de domínio em modules
### Antes
```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/products')
def products():
    rows = db.execute('SELECT * FROM products').fetchall()
    return jsonify([dict(row) for row in rows])
```

### Depois
```python
# controllers/product_controller.py
from models.product_model import get_all_products

def list_products():
    return get_all_products()
```

```python
# routes/product_routes.py
from flask import Blueprint, jsonify
from controllers.product_controller import list_products

bp = Blueprint('products', __name__)

@bp.route('/products')
def products():
    data = list_products()
    return jsonify(data)
```

```python
# models/product_model.py
from database import db

def get_all_products():
    rows = db.execute('SELECT * FROM products').fetchall()
    return [dict(row) for row in rows]
```

## 2. Fat Controller / Business Logic in Routes → Controller + Model
### Antes
```js
app.post('/checkout', async (req, res) => {
  const { userId, items } = req.body;
  const user = await db.query(`SELECT * FROM users WHERE id = ${userId}`);
  const order = await db.query(`INSERT INTO orders (...) VALUES (...) RETURNING *`);
  res.json({ order });
});
```

### Depois
```js
// controllers/checkoutController.js
import { createOrder } from '../models/orderModel.js';

export async function checkout(req, res, next) {
  const order = await createOrder(req.body);
  res.json({ order });
}
```

```js
// models/orderModel.js
import db from '../database/db.js';

export async function createOrder(payload) {
  const { userId, items } = payload;
  return db.query('INSERT INTO orders (...) VALUES (...) RETURNING *', [userId, JSON.stringify(items)]);
}
```

## 3. Hardcoded Secrets → Config / Environment
### Antes
```python
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
```

### Depois
```python
# config/settings.py
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///dev.db')
```

```python
# app.py
from config.settings import SECRET_KEY, DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
```

## 4. SQL Injection / Query Concatenation → Query Parameterization
### Antes
```js
const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;
const result = await db.query(query);
```

### Depois
```js
const query = 'SELECT * FROM users WHERE email = $1';
const result = await db.query(query, [req.body.email]);
```

## 5. Deprecated API Usage → Modern equivalent
### Antes (Express)
```js
const bodyParser = require('body-parser');
app.use(bodyParser.json());
```

### Depois
```js
app.use(express.json());
```

### Antes (Flask)
```python
from flask import Flask, jsonify
from flask.ext.cors import CORS
```

### Depois
```python
from flask import Flask, jsonify
from flask_cors import CORS
```

## 6. Shared Global State → Encapsular em classes/serviços
### Antes
```python
cache = {}

@app.route('/count')
def count():
    cache['count'] = cache.get('count', 0) + 1
    return jsonify(cache)
```

### Depois
```python
# services/counter_service.py
class CounterService:
    def __init__(self):
        self._count = 0

    def increment(self):
        self._count += 1
        return self._count

counter_service = CounterService()
```

```python
# controllers/counter_controller.py
from services.counter_service import counter_service

def next_count():
    return counter_service.increment()
```

## 7. Missing Input Validation → Centralizar validação
### Antes
```js
app.post('/tasks', async (req, res) => {
  const task = req.body;
  const result = await createTask(task);
  res.json(result);
});
```

### Depois
```js
import { validateTaskPayload } from '../middlewares/validation.js';

router.post('/tasks', validateTaskPayload, taskController.createTask);
```

```js
// middlewares/validation.js
export function validateTaskPayload(req, res, next) {
  const { title } = req.body;
  if (!title) {
    return res.status(400).json({ error: 'title is required' });
  }
  next();
}
```

## 8. Duplicate Logic → Reutilizar funções comuns
### Antes
```python
def format_user(user):
    return {'id': user['id'], 'name': user['name']}

# em outro arquivo
def format_customer(customer):
    return {'id': customer['id'], 'name': customer['name']}
```

### Depois
```python
# utils/serializers.py

def serialize_user(user):
    return {'id': user['id'], 'name': user['name']}
```

```python
from utils.serializers import serialize_user
```

## 9. Composition Root → Centralizar inicialização
### Antes
```js
const app = express();
app.use(router);
app.listen(3000);
```

### Depois
```js
// app.js
import express from 'express';
import routes from './routes/index.js';
import { configureDatabase } from './config/db.js';

const app = express();
configureDatabase();
app.use(express.json());
app.use(routes);
export default app;
```

## 10. Controller should return data, route should send response
### Antes
```python
@app.route('/users')
def users():
    return jsonify(get_users())
```

### Depois
```python
# controllers/user_controller.py
from models.user_model import get_all_users

def list_users():
    return get_all_users()
```

```python
# routes/user_routes.py
from flask import Blueprint, jsonify
from controllers.user_controller import list_users

bp = Blueprint('users', __name__)

@bp.route('/users')
def users():
    data = list_users()
    return jsonify(data)
```

## Uso do playbook
1. Identifique o anti-pattern.
2. Encontre o módulo e as linhas correspondentes.
3. Aplique a transformação proposta.
4. Execute a validação: boot da aplicação e teste de endpoints.
