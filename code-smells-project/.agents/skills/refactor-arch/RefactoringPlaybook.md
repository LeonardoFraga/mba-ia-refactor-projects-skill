# RefactoringPlaybook

Este playbook descreve transformações concretas para os anti-patterns do catálogo, com exemplos de antes/depois para as linguagens suportadas.

---

## 1. God Class / God File → Extração de domínio em modules

### Python/Flask

**Antes:**
```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/products')
def products():
    rows = db.execute('SELECT * FROM products').fetchall()
    return jsonify([dict(row) for row in rows])
```

**Depois:**
```python
# controllers/product_controller.py
from models.product_model import get_all_products

def list_products():
    return get_all_products()
```

### Node.js/Express

**Antes:**
```js
const app = express();
app.get('/products', async (req, res) => {
  const rows = await db.query('SELECT * FROM products');
  res.json(rows);
});
```

**Depois:**
```js
// controllers/productController.js
import { getAllProducts } from '../models/productModel.js';

export async function listProducts(req, res) {
  const products = await getAllProducts();
  res.json(products);
}
```

### Java/Spring Boot

**Antes:**
```java
@RestController
@RequestMapping("/products")
public class ProductController {
  @Autowired private JdbcTemplate jdbc;
  
  @GetMapping
  public List<Product> list() {
    return jdbc.query("SELECT * FROM products", (rs, row) -> 
      new Product(rs.getLong("id"), rs.getString("name"))
    );
  }
}
```

**Depois:**
```java
// models/Product.java
@Entity
@Table(name = "products")
public class Product {
  @Id private Long id;
  private String name;
  // getters/setters
}

// repositories/ProductRepository.java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {}

// services/ProductService.java
@Service
public class ProductService {
  @Autowired private ProductRepository repo;
  
  public List<Product> getAllProducts() {
    return repo.findAll();
  }
}

// controllers/ProductController.java
@RestController
@RequestMapping("/products")
public class ProductController {
  @Autowired private ProductService service;
  
  @GetMapping
  public List<Product> list() {
    return service.getAllProducts();
  }
}
```

### C#/.NET/ASP.NET Core

**Antes:**
```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductController : ControllerBase {
  [HttpGet]
  public async Task<IActionResult> GetAll() {
    using (var conn = new SqlConnection(_connString)) {
      var cmd = conn.CreateCommand();
      cmd.CommandText = "SELECT * FROM Products";
      conn.Open();
      var reader = cmd.ExecuteReader();
      var products = new List<Product>();
      while (reader.Read()) {
        products.Add(new Product { Id = (int)reader["Id"], Name = (string)reader["Name"] });
      }
      return Ok(products);
    }
  }
}
```

**Depois:**
```csharp
// Models/Product.cs
public class Product {
  public int Id { get; set; }
  public string Name { get; set; }
}

// Data/ProductRepository.cs
public interface IProductRepository {
  Task<List<Product>> GetAllAsync();
}

public class ProductRepository : IProductRepository {
  private readonly AppDbContext _context;
  
  public ProductRepository(AppDbContext context) {
    _context = context;
  }
  
  public async Task<List<Product>> GetAllAsync() {
    return await _context.Products.ToListAsync();
  }
}

// Services/ProductService.cs
public interface IProductService {
  Task<List<Product>> GetAllProductsAsync();
}

public class ProductService : IProductService {
  private readonly IProductRepository _repo;
  
  public ProductService(IProductRepository repo) {
    _repo = repo;
  }
  
  public async Task<List<Product>> GetAllProductsAsync() {
    return await _repo.GetAllAsync();
  }
}

// Controllers/ProductController.cs
[ApiController]
[Route("api/[controller]")]
public class ProductController : ControllerBase {
  private readonly IProductService _service;
  
  public ProductController(IProductService service) {
    _service = service;
  }
  
  [HttpGet]
  public async Task<IActionResult> GetAll() {
    var products = await _service.GetAllProductsAsync();
    return Ok(products);
  }
}
```

---

## 2. Fat Controller / Business Logic in Routes → Controller + Model

### Python/Flask

**Antes:**
```python
@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = request.json['user_id']
    items = request.json['items']
    user = db.execute(f'SELECT * FROM users WHERE id = {user_id}').fetchone()
    total = sum([item['price'] * item['qty'] for item in items])
    order_id = db.execute(
        f"INSERT INTO orders (user_id, total) VALUES ({user_id}, {total}) RETURNING id"
    ).fetchone()['id']
    return jsonify({'order_id': order_id})
```

**Depois:**
```python
# controllers/checkout_controller.py
from models.order_model import create_order
from models.user_model import get_user

def process_checkout(payload):
    user = get_user(payload['user_id'])
    total = sum([item['price'] * item['qty'] for item in payload['items']])
    order = create_order(user['id'], total, payload['items'])
    return order
```

### Node.js/Express

**Antes:**
```js
app.post('/checkout', async (req, res) => {
  const { userId, items } = req.body;
  const user = await db.query(`SELECT * FROM users WHERE id = ${userId}`);
  const total = items.reduce((sum, item) => sum + (item.price * item.qty), 0);
  const order = await db.query(
    `INSERT INTO orders (user_id, total) VALUES (${userId}, ${total}) RETURNING *`
  );
  res.json({ order });
});
```

**Depois:**
```js
// controllers/checkoutController.js
import { createOrder } from '../models/orderModel.js';
import { getUser } from '../models/userModel.js';

export async function checkout(req, res, next) {
  try {
    const { userId, items } = req.body;
    const user = await getUser(userId);
    const total = items.reduce((sum, item) => sum + (item.price * item.qty), 0);
    const order = await createOrder(user.id, total, items);
    res.status(201).json({ order });
  } catch (error) {
    next(error);
  }
}
```

### Java/Spring Boot

**Antes:**
```java
@RestController
@RequestMapping("/orders")
public class OrderController {
  @Autowired private JdbcTemplate jdbc;
  
  @PostMapping("/checkout")
  public ResponseEntity<?> checkout(@RequestBody CheckoutRequest req) {
    Long userId = req.getUserId();
    List<OrderItem> items = req.getItems();
    double total = items.stream().mapToDouble(i -> i.getPrice() * i.getQty()).sum();
    jdbc.update(
      "INSERT INTO orders (user_id, total) VALUES (?, ?)",
      userId, total
    );
    return ResponseEntity.ok(Map.of("status", "ok"));
  }
}
```

**Depois:**
```java
// services/OrderService.java
@Service
public class OrderService {
  @Autowired private OrderRepository orderRepo;
  @Autowired private UserRepository userRepo;
  
  public Order processCheckout(CheckoutRequest req) {
    User user = userRepo.findById(req.getUserId()).orElseThrow();
    double total = req.getItems().stream()
      .mapToDouble(i -> i.getPrice() * i.getQty()).sum();
    
    Order order = new Order();
    order.setUser(user);
    order.setTotal(total);
    order.setItems(req.getItems());
    
    return orderRepo.save(order);
  }
}

// controllers/OrderController.java
@RestController
@RequestMapping("/orders")
public class OrderController {
  @Autowired private OrderService orderService;
  
  @PostMapping("/checkout")
  public ResponseEntity<?> checkout(@RequestBody CheckoutRequest req) {
    Order order = orderService.processCheckout(req);
    return ResponseEntity.status(201).body(order);
  }
}
```

---

## 3. Hardcoded Secrets → Config / Environment

### Python/Flask

**Antes:**
```python
app.config['SECRET_KEY'] = 'my-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
```

**Depois:**
```python
# config/settings.py
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-dev-key')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///dev.db')
```

### Node.js/Express

**Antes:**
```js
const dbConfig = {
  host: 'localhost',
  user: 'root',
  password: 'super-secret',
  database: 'myapp'
};
```

**Depois:**
```js
// config/db.js
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || 'myapp'
};
```

### Java/Spring Boot

**Antes:**
```properties
# application.properties
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=secret123
```

**Depois:**
```properties
# application.properties (no Git)
spring.datasource.url=${DB_URL}
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
```

### C#/.NET

**Antes:**
```csharp
public class AppDbContext : DbContext {
  protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder) {
    optionsBuilder.UseSqlServer("Server=localhost;Database=mydb;User=sa;Password=secret123");
  }
}
```

**Depois:**
```csharp
// In Program.cs or Startup.cs
var connectionString = configuration.GetConnectionString("DefaultConnection");
services.AddDbContext<AppDbContext>(options =>
  options.UseSqlServer(connectionString)
);

// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=...;Database=...;User=...;Password=..."
  }
}
```

---

## 4. SQL Injection / Query Concatenation → Parameterized Queries

### Python/Flask

**Antes:**
```python
email = request.json['email']
user = db.execute(f"SELECT * FROM users WHERE email = '{email}'").fetchone()
```

**Depois:**
```python
email = request.json['email']
user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
```

### Node.js/Express

**Antes:**
```js
const email = req.body.email;
const user = await db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

**Depois:**
```js
const email = req.body.email;
const user = await db.query('SELECT * FROM users WHERE email = ?', [email]);
```

### Java/Spring Boot

**Antes:**
```java
String email = req.getEmail();
List<User> users = jdbc.query(
  "SELECT * FROM users WHERE email = '" + email + "'",
  new UserMapper()
);
```

**Depois:**
```java
String email = req.getEmail();
List<User> users = jdbc.query(
  "SELECT * FROM users WHERE email = ?",
  new UserMapper(),
  email
);
```

---

## 5. Deprecated API Usage → Modern Equivalent

### Python/Flask

**Antes:**
```python
from flask.ext.cors import CORS
from flask import Flask, jsonify
```

**Depois:**
```python
from flask_cors import CORS
from flask import Flask, jsonify
```

### Node.js/Express

**Antes:**
```js
const bodyParser = require('body-parser');
app.use(bodyParser.json());

app.get('/user/:id', (req, res) => {
  const id = req.param('id');
});
```

**Depois:**
```js
app.use(express.json());

app.get('/user/:id', (req, res) => {
  const id = req.params.id;
});
```

---

## 6. Shared Global State → Encapsular em classes/serviços

### Python/Flask

**Antes:**
```python
cache = {}

@app.route('/count')
def count():
    cache['count'] = cache.get('count', 0) + 1
    return jsonify(cache)
```

**Depois:**
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

---

## 7. Missing Input Validation → Centralizar validação

### Python/Flask

**Antes:**
```python
@app.route('/tasks', methods=['POST'])
def create():
    task = request.json
    result = save_task(task)
    return jsonify(result)
```

**Depois:**
```python
# middlewares/validation.py
from functools import wraps

def validate_task(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.json or {}
        if not data.get('title'):
            return jsonify({'error': 'title is required'}), 400
        return f(*args, **kwargs)
    return decorated_function

# routes/task_routes.py
@bp.route('/tasks', methods=['POST'])
@validate_task
def create():
    task = request.json
    result = save_task(task)
    return jsonify(result)
```

### Node.js/Express

**Antes:**
```js
app.post('/tasks', async (req, res) => {
  const task = req.body;
  const result = await createTask(task);
  res.json(result);
});
```

**Depois:**
```js
// middlewares/validation.js
export function validateTaskPayload(req, res, next) {
  const { title } = req.body;
  if (!title) {
    return res.status(400).json({ error: 'title is required' });
  }
  next();
}

// routes/taskRoutes.js
router.post('/tasks', validateTaskPayload, taskController.createTask);
```

---

## 8. Duplicate Logic → Reutilizar funções comuns

### Python/Flask

**Antes:**
```python
def format_user(user):
    return {'id': user['id'], 'name': user['name']}

def format_customer(customer):
    return {'id': customer['id'], 'name': customer['name']}
```

**Depois:**
```python
# utils/serializers.py
def serialize_person(person):
    return {'id': person['id'], 'name': person['name']}

# Em controllers
from utils.serializers import serialize_person
```

---

## Como usar este playbook

1. Identifique o anti-pattern no relatório (Fase 2)
2. Encontre a transformação correspondente aqui
3. Adapte o exemplo para seu projeto específico
4. Aplique a mudança
5. Valide: boot da aplicação e teste de endpoints

---

## Extensão para outras linguagens

Esta skill cobre completamente:
- ✅ Python/Flask
- ✅ Node.js/Express
- ✅ Java/Spring Boot
- ✅ C#/.NET/ASP.NET Core

Para estender para outras linguagens (Go, Rust, Kotlin, PHP, Ruby, etc.):

### Passo 1: Expandir `ProjectAnalyses.md`
Adicione uma seção framework-específica com:
- Sinais de detecção (imports, arquivo manifesto)
- Estrutura MVC esperada
- Anti-patterns comuns nessa linguagem

### Passo 2: Adicionar exemplos em `RefactoringPlaybook.md`
Para cada anti-pattern, adicione antes/depois em sua linguagem-alvo

### Passo 3: Atualizar `ArchitecturalGuidelines.md`
Documente convenções, padrões de injeção de dependência, etc. da linguagem

### Passo 4: Testar em um projeto real
Garanta que a skill detecte corretamente a linguagem, framework e anti-patterns
