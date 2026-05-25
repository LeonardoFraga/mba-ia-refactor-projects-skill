# AntiPatternCatalog

Este catálogo define anti-patterns comuns em aplicações backend, com sinais de detecção, impacto e severidade. Ele serve como base para a Fase 2 da skill, permitindo mapear cada problema em código real para um relatório de auditoria.

## Severidade
- **CRITICAL:** Falhas arquiteturais ou de segurança que quebram funcionalidade, expõem dados ou impedem manutenção.
- **HIGH:** Violação grave de separação de responsabilidades, acoplamento forte ou código difícil de testar.
- **MEDIUM:** Problemas de manutenibilidade, performance moderada ou duplicação que degradam qualidade sem quebrar imediatamente.
- **LOW:** Melhorias de legibilidade, nomenclatura e padronização.

## Anti-patterns

### 1. God Class / God File
- Severidade: CRITICAL
- Sinais de detecção:
  - Um único arquivo contém rotas, lógica de negócio, acesso a dados e validações.
  - Funções longas (>100 linhas) que fazem múltiplas responsabilidades.
  - Importações de `flask`, `sqlalchemy`, `pandas`, `mysql`, `pg` ou `mongodb` no mesmo módulo de rota.
- Impacto:
  - Dificulta testes e evolução.
  - Alterações em um domínio afetam vários comportamentos.

### 2. Fat Controller / Business Logic in Routes
- Severidade: HIGH
- Sinais de detecção:
  - Rota processa payload, valida, consulta banco e monta resposta sem delegar a uma camada de serviço/model.
  - Express: `app.post('/x', async (req, res) => { ... })` com SQL inline.
  - Flask: `@app.route` com loops, branches e consultas SQL diretas.
- Impacto:
  - Fraca reutilização e difícil instrumentação.

### 3. Hardcoded Secrets / Config
- Severidade: CRITICAL
- Sinais de detecção:
  - Strings como `SECRET_KEY`, `DB_PASSWORD`, `API_KEY`, `JWT_SECRET` em código-fonte.
  - Configuração de host, porta ou credenciais escritas diretamente em `app.py`, `config.py`, `server.js`.
- Impacto:
  - Risco de vazamento e impedimento à configuração em diferentes ambientes.

### 4. SQL/NoSQL Injection via Concatenation
- Severidade: CRITICAL
- Sinais de detecção:
  - Queries construídas com concatenação de strings ou templates: `"SELECT * FROM users WHERE id=" + id`.
  - Uso de `req.body`, `params`, `request.args` diretamente em strings SQL.
- Impacto:
  - Vulnerabilidade de segurança grave.

### 5. Deprecated API Usage
- Severidade: MEDIUM
- Sinais de detecção:
  - Node.js/Express: `bodyParser.json()`, `req.param`, `app.configure`, `express.Router()` sem `new` em versões antigas.
  - Python/Flask: `Flask.jsonify` com tipos não suportados, `flask.ext` imports, `werkzeug.exceptions` obsoletos.
  - Pacotes de banco de dados antigos (`mysql`, `pg` sem pool, `sqlite3` raw sem context manager).
- Impacto:
  - Código quebrará em upgrades e usa práticas não suportadas.

### 6. Shared Global State
- Severidade: HIGH
- Sinais de detecção:
  - Variáveis globais mutáveis definidas fora de funções e atualizadas por múltiplas rotas.
  - Objetos únicos exportados/importados como `state`, `cache`, `current_user` sem encapsulamento.
- Impacto:
  - Condições de corrida, comportamento não determinístico e difícil depuração.

### 7. Missing Input Validation in Routes
- Severidade: MEDIUM
- Sinais de detecção:
  - Rotas que aceitam payloads sem checar campos obrigatórios ou tipos.
  - Chamadas diretas a `request.json`, `req.body` e uso imediato sem validação.
- Impacto:
  - Erros silenciosos, falhas em produção e exposição de inconsistências.

### 8. Duplicate Query / Duplicate Logic
- Severidade: MEDIUM
- Sinais de detecção:
  - Cópia de trechos SQL ou chamadas a banco em vários arquivos.
  - Lógica de transformação de dados repetida em diferentes rotas.
- Impacto:
  - Manutenção custosa e maior risco de divergência.

### 9. Tight Coupling Between Layers
- Severidade: HIGH
- Sinais de detecção:
  - Controllers importam classes de banco de dados ou dependem diretamente de implementações concretas.
  - Models acessam `request`, `res`, `session` ou `req` do framework.
- Impacto:
  - Reduz a testabilidade e impede reorganização da arquitetura.

### 10. Routes as Views / Presentation Logic in API Layer
- Severidade: LOW
- Sinais de detecção:
  - Rota monta JSON com formatação e markup em vez de liberar essa responsabilidade para controllers ou serializers.
  - Mistura de mensagens de erro, códigos HTTP e payloads em um único bloco.
- Impacto:
  - Legibilidade prejudicada e necessidade de extração posterior.

## Como usar este catálogo
1. Busque sinais de detecção no código.
2. Classifique o problema por severidade.
3. Gere um finding no relatório com arquivo, linhas e recomendação.
4. Use o playbook de refatoração para aplicar a mudança.
