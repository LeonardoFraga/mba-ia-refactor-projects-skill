# ProjectAnalyses

Este documento guia a Fase 1 da skill: analisar o projeto e identificar linguagem, framework, arquitetura, domínio e dependências.

A estratégia é dividida em **padrões genéricos** (aplicáveis a qualquer linguagem) e **padrões específicos por framework** (requerem cobertura explícita).

---

## Padrões Genéricos (funciona em qualquer linguagem)

Esses sinais são universais e não dependem de framework específico:

### Detecção de God Class / Arquivo Monolítico
- Um único arquivo > 300-500 linhas
- Contém mistura de:
  - Definição de rotas/endpoints
  - Lógica de validação
  - Queries ao banco de dados
  - Mapeamento de domínio
- Múltiplas funções/métodos fazendo coisas diferentes

### Detecção de Fat Controller
- Rotas que processam entrada, validam, consultam BD e montam resposta em uma única função
- Ausência de delegação para models/services
- Exemplos:
  - Flask: `@app.route('/x') def handler(): ... db.query(...) ... validate(...) ... return response`
  - Express: `app.post('/x', async (req, res) => { ... db.query() ... validation ... res.json() })`
  - Spring: `@PostMapping("/x") public ResponseEntity<?> handle(Request req) { ... repo.save() ... }`

### Detecção de Hardcoded Secrets
- Strings sensíveis em código-fonte: `SECRET_KEY`, `DB_PASSWORD`, `API_KEY`, `JWT_SECRET`
- Configuração de conexão inline: `host:port`, `connection_string`
- Padrão de procura: variáveis nomeadas com `secret|password|key|token|credential` com valores não interpolados

### Detecção de SQL/Query Injection
- Queries construídas via concatenação de strings
- Uso direto de variáveis/params em strings de query
- Exemplos:
  - `"SELECT * FROM users WHERE id=" + id`
  - `` `INSERT INTO orders (...) VALUES (${userId})` ``
  - `"SELECT * FROM users WHERE email='" + req.body.email + "'"` 

### Detecção de Shared Global State
- Variáveis globais mutáveis atualizadas por múltiplos handlers
- Objetos singleton sem encapsulamento (`state = {}`, `cache = {}`)
- Importação e mutação de variáveis globais em múltiplos lugares

### Detecção de Duplicate Logic
- Mesma lógica de transformação repetida em múltiplas rotas
- Queries SQL idênticas em vários arquivos
- Funções de formatação/serialização repetidas

### Detecção de Missing Input Validation
- Rotas que aceitam payloads sem verificação de campos obrigatórios
- Acesso direto a `request.data`, `request.json`, `req.body` sem schema/validator
- Transformação ou lógica aplicada antes de validação

### Detecção de Tight Coupling
- Controllers importam e usam diretamente classes de BD (model classes)
- Controllers instanciam dependências em vez de recebê-las
- Models importam e usam objetos HTTP (request, response, session)

---

## Detecção Específica por Framework

Essas heurísticas requerem conhecimento explícito de cada framework.

### Python / Flask

#### Sinais de Flask:
- `from flask import Flask`, `from flask import Blueprint`
- `app = Flask(__name__)` ou `@app.route(...)`
- Arquivos de manifesto: `requirements.txt` com `flask`, `flask-cors`, `flask-sqlalchemy`

#### Banco de dados:
- ORM: `from sqlalchemy import`, `flask_sqlalchemy`, `Flask-SQLAlchemy`
- Raw: `import sqlite3`, `import pymysql`, `import psycopg2`
- Queries inline: `db.execute("SELECT ...")`, `cursor.execute("INSERT ...")`

#### Estrutura esperada (MVC):
```
app.py                    # Raiz, inicialização
config/settings.py        # Configuração
models/user_model.py      # Models
controllers/user_controller.py  # Controllers
routes/user_routes.py     # Rotas (Blueprints)
```

#### Anti-patterns Flask comuns:
- Importação deprecated: `from flask.ext.cors import CORS` (deve ser `from flask_cors import CORS`)
- Blueprints definidos e registrados no mesmo arquivo que rota
- SQLAlchemy queries diretas em rotas

### Node.js / Express

#### Sinais de Express:
- `require('express')` ou `import express from 'express'`
- `const app = express()`, `app.listen()`, `app.use()`
- `module.exports = app` ou `router = express.Router()`
- Arquivos de manifesto: `package.json` com `express`, `cors`, dependências de BD

#### Banco de dados:
- SQL: `mysql`, `mysql2`, `pg`, `sqlite3`, `better-sqlite3`
- ORM: `sequelize`, `typeorm`, `knex`, `prisma`
- NoSQL: `mongoose`, `redis`, `mongodb`
- Queries inline: `` db.query(`SELECT ...`) `` ou `connection.query('INSERT ...')`

#### Estrutura esperada (MVC):
```
server.js ou app.js       # Raiz
config/db.js              # Configuração
models/user.js            # Models
controllers/userController.js  # Controllers
routes/userRoutes.js      # Rotas
```

#### Anti-patterns Express comuns:
- `bodyParser.json()` (deve usar `express.json()` direto)
- `req.param()` (deprecated, usar `req.params` ou `req.query`)
- Queries SQL diretas em rotas: `app.post('/users', async (req, res) => { db.query(...) })`

### Java / Spring Boot

#### Sinais de Spring Boot:
- `@SpringBootApplication`, `@RestController`, `@Service`, `@Repository`
- Imports: `org.springframework.boot.*`, `org.springframework.web.bind.annotation.*`
- Arquivos de manifesto: `pom.xml` com `spring-boot-starter-web`, `spring-boot-starter-data-jpa`
- `application.properties` ou `application.yml`

#### Banco de dados:
- ORM: `JPA/Hibernate`, `Spring Data JPA`, `MyBatis`
- Drivers: `mysql-connector-java`, `postgresql`, `h2`
- Queries: `@Query("SELECT ...")`, `entityManager.createQuery()`, `JdbcTemplate.query()`

#### Estrutura esperada (MVC):
```
src/main/java/com/example/
  Application.java         # Raiz
  config/AppConfig.java    # Configuração
  models/User.java         # Entities/Models
  controllers/UserController.java  # Controllers
  services/UserService.java        # Services (camada extra)
  repositories/UserRepository.java # Data access
```

#### Anti-patterns Spring comuns:
- `@Autowired` em campos (use constructor injection)
- Business logic direto em `@Controller` (deve estar em `@Service`)
- Raw SQL queries (deve usar `@Query` ou JPA Criteria)
- Entity classes com getters/setters poluídos e lógica de domínio

### C# / ASP.NET Core

#### Sinais de ASP.NET Core:
- `[ApiController]`, `[Route(...)]`, `[HttpGet]`, `[HttpPost]`
- Imports: `using Microsoft.AspNetCore.*`, `using System.Collections.Generic`
- `Startup.cs` ou `Program.cs` com `services.AddControllers()`, `app.MapControllers()`
- Arquivos: `.csproj` com `Microsoft.AspNetCore.App`

#### Banco de dados:
- ORM: `Entity Framework Core`, `Dapper`, `NHibernate`
- Drivers: `SqlServer`, `MySql.Data`, `Npgsql`
- Queries: `DbContext`, `SqlCommand`, `IQueryable<T>`

#### Estrutura esperada (MVC):
```
Program.cs ou Startup.cs  # Raiz e composição
Models/User.cs            # Models/Entities
Controllers/UserController.cs  # Controllers
Services/UserService.cs        # Services
Data/AppDbContext.cs           # DbContext
```

#### Anti-patterns .NET comuns:
- DbContext criado sem using/disposal adequado
- Business logic direto em `[ApiController]` (deve estar em `[Service]`)
- SQL strings concatenadas (deve usar Parametrized Queries)
- N+1 queries sem `.Include()` ou carregamento explícito

---

## Detecção de domínio

Extraia o domínio analisando:
- Nomes de entidades: `user`, `task`, `product`, `pedido`, `order`, `checkout`
- Padrões de rota: `/users`, `/tasks`, `/products`, `/orders`, `/checkout`
- Variáveis e comentários: "Task Manager", "E-commerce", "LMS", "checkout flow"

## Mapeamento de arquitetura

### Monolítica / Arquivo único:
- Tudo em 1-4 arquivos
- Sem separação clara de camadas
- Exemplo: `app.py` com rotas, models, queries

### Parcialmente separada:
- Projeto já tem `models/`, `routes/`, `controllers/`
- Mas responsabilidades podem estar mescladas
- Exemplo: `task-manager-api` com `models/`, `routes/`, `services/`

### MVC bem organizado:
- `app.py`/`server.js` é apenas raiz
- Controllers, models, routes em diretórios distintos
- Sem imports circulares

## Checklist de Fase 1
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade
- [ ] Dependências e banco de dados identificados
- [ ] Arquitetura atual mapeada como monolítica, parcialmente separada ou MVC

## Formato de saída esperado
A análise deve gerar um resumo com:
- Linguagem
- Framework
- Versão do framework
- Dependências principais
- Domínio de negócio
- Arquitetura atual
- Diretórios e arquivos analisados
- Banco de dados detectado
