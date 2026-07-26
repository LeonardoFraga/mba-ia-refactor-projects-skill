# Skill de Auditoria e Refatoração Arquitetural — `refactor-arch`

Skill agnóstica de tecnologia que audita e refatora projetos backend para o padrão
**MVC**, em três fases: **Análise → Auditoria → Refatoração**. Foi construída uma
única vez e copiada para os três projetos-alvo (Python/Flask ×2 e Node/Express ×1),
provando que é genuinamente reutilizável.

> A skill vive em `.claude/skills/refactor-arch/` dentro de cada projeto:
> `SKILL.md` (o orquestrador das 3 fases) + `references/` com 5 arquivos de
> conhecimento (análise, catálogo de anti-patterns, template de relatório,
> guidelines de MVC e playbook de refatoração).

---

## A) Análise Manual

Antes de construir a skill, li o código dos três projetos e documentei os
problemas de maior impacto. Cada tabela cobre o mínimo exigido: **≥5 problemas**,
sendo **≥1 CRITICAL/HIGH, ≥2 MEDIUM e ≥2 LOW**.

### Projeto 1 — `code-smells-project` (Python/Flask, E-commerce)

Monolito de 4 arquivos (~800 linhas). Tudo misturado: rotas, regra de negócio,
SQL e validação.

| # | Severidade | Problema | Local | Por que é relevante |
|---|-----------|----------|-------|---------------------|
| 1 | **CRITICAL** | SQL Injection por concatenação de string | `models.py:28,48,58,68,92,109-110,126-128,140,155,174,280,289-297` | Entrada do usuário entra direto na query (`"... WHERE id = " + str(id)`, login com email/senha concatenados). Permite dump/alteração de todo o banco. |
| 2 | **CRITICAL** | `SECRET_KEY` e `DEBUG` hardcoded | `app.py:7-8` | Segredo versionado no código e debug ligado em "produção"; vazamento de credencial e stack traces expostos. |
| 3 | **CRITICAL** | Endpoint executa SQL arbitrário do corpo da request | `app.py:59-78` (`/admin/query`) | Qualquer cliente executa `DELETE`/`DROP` no banco sem autenticação. RCE de banco. |
| 4 | **CRITICAL** | God File + senha em texto puro exposta | `models.py:1-315`; senha retornada em `get_todos_usuarios` (`models.py:83`) e `secret_key` vazado em `/health` (`controllers.py:289`) | Um arquivo com 4 domínios impossível de testar; senhas em claro devolvidas pela API. |
| 5 | **HIGH** | Regra de negócio pesada + efeitos colaterais no fluxo | `models.py:133-169` (cria pedido, calcula total, baixa estoque) e `controllers.py:208-210` (dispara "email/SMS/push" via `print`) | Lógica de checkout presa no model/controller, sem serviço; efeitos colaterais não isoláveis nem testáveis. |
| 6 | **HIGH** | Estado global mutável de conexão | `database.py:4` (`db_connection` global) | Conexão única compartilhada entre threads (`check_same_thread=False`), fonte de race conditions. |
| 7 | **MEDIUM** | Queries N+1 na montagem de pedidos | `models.py:187-199` e `203-231` | Para cada pedido, uma query por item e outra por produto — custo explode com o volume. |
| 8 | **MEDIUM** | Lógica duplicada | `get_pedidos_usuario` vs `get_todos_pedidos` (`models.py:171-233`) | Dois blocos quase idênticos de serialização; manutenção divergente. |
| 9 | **LOW** | `print()` de debug espalhados como logging | `controllers.py:8,11,57,161,179,208-210,248` | Poluição e ausência de logging estruturado. |
| 10 | **LOW** | Magic values e `except` genérico | `controllers.py:52` (lista de categorias inline), `except Exception` em toda rota | Legibilidade e tratamento de erro pobre. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS + checkout)

3 arquivos, ~180 linhas. SQLite em memória. Uma classe "Frankenstein".

| # | Severidade | Problema | Local | Por que é relevante |
|---|-----------|----------|-------|---------------------|
| 1 | **CRITICAL** | Segredos hardcoded (senha de banco, chave de pagamento, SMTP) | `src/utils.js:2-5` (`dbPass`, `paymentGatewayKey: 'pk_live_...'`, `smtpUser`) | Chave de gateway **de produção** (`pk_live`) versionada; vazamento imediato. |
| 2 | **CRITICAL** | Criptografia quebrada + dados sensíveis logados | `src/utils.js:17-23` (`badCrypto`); `src/AppManager.js:45` loga número do cartão e a chave do gateway | Hash inseguro/reversível para senhas e PAN de cartão impresso no console (violação PCI). |
| 3 | **HIGH** | God Class `AppManager` | `src/AppManager.js:4-141` | Uma classe é dona da conexão do banco, define todas as rotas e concentra toda a lógica — zero separação de camadas. |
| 4 | **HIGH** | Fat Controller / callback hell no checkout | `src/AppManager.js:28-78` | Um handler valida, consulta curso, cria usuário, processa pagamento, matricula, insere pagamento, grava auditoria e cacheia — tudo aninhado. |
| 5 | **HIGH** | Estado global mutável | `src/utils.js:9-10` (`globalCache`, `totalRevenue`) | Estado compartilhado entre requisições; race conditions e comportamento não determinístico. |
| 6 | **MEDIUM** | N+1 no relatório financeiro | `src/AppManager.js:89-127` | `forEach` aninhado consulta usuário e pagamento por matrícula — explode com o número de alunos. |
| 7 | **MEDIUM** | Integridade referencial quebrada no delete | `src/AppManager.js:131-137` | `DELETE /api/users/:id` remove o usuário e deixa matrículas/pagamentos órfãos (o próprio código admite: "ficaram sujos no banco"). |
| 8 | **LOW** | Nomes de variável ruins | `src/AppManager.js:29-33` (`u`, `e`, `p`, `cid`, `cc`) | Ilegível; esconde a intenção. |
| 9 | **LOW** | API legada/deprecated do driver | `src/AppManager.js:1` (`sqlite3.verbose()` + callbacks crus) | Estilo callback legado; equivalente moderno é driver promisificado / `better-sqlite3`. |

### Projeto 3 — `task-manager-api` (Python/Flask + SQLAlchemy, Task Manager)

Já **parcialmente organizado** (`models/`, `routes/`, `services/`, `utils/`,
~1150 linhas) — mas com vazamentos de camada e defeitos de segurança.

| # | Severidade | Problema | Local | Por que é relevante |
|---|-----------|----------|-------|---------------------|
| 1 | **CRITICAL** | Hash de senha com MD5 | `models/user.py:29,32` | MD5 é quebrado para senhas; hashes recuperáveis por rainbow tables. |
| 2 | **CRITICAL** | Senha exposta na serialização | `models/user.py:16-25` (`to_dict` inclui `password`) | O hash da senha é devolvido por `/users`, `/users/<id>`, `/login`. Vazamento de credencial via API. |
| 3 | **HIGH** | Segredos hardcoded (app + SMTP) | `app.py:13` (`SECRET_KEY`); `services/notification_service.py:9-10` (`email_password='senha123'`) | Credenciais versionadas em dois pontos. |
| 4 | **HIGH** | Lógica de negócio/serialização nas rotas + N+1 | `routes/task_routes.py:16-60` (monta dict e faz `User.query.get`/`Category.query.get` por task); `routes/report_routes.py:53-68` (query por usuário em loop) | Rotas "gordas" com N+1; deveria ser controller/serviço + eager loading. |
| 5 | **MEDIUM** | Lógica de "overdue" duplicada | `models/task.py:50-60`, `routes/task_routes.py:30-39,71-80`, `routes/user_routes.py:171-180`, `routes/report_routes.py:34-43` | Mesma regra reescrita 4×; divergência garantida. |
| 6 | **MEDIUM** | `except:` genérico engolindo erros | `routes/task_routes.py:62`; `routes/user_routes.py:130`; `routes/report_routes.py:186,208,222` | Mascara falhas reais, dificulta diagnóstico. |
| 7 | **LOW** | API deprecated: `datetime.utcnow()` e `Query.get()` | `datetime.utcnow()` em models/routes/seed; `Model.query.get()` em várias rotas | `utcnow()` deprecated no Python 3.12+; `Query.get()` legado no SQLAlchemy 2.x (use `db.session.get`). |
| 8 | **LOW** | Imports não usados | `routes/task_routes.py:7` (`json, os, sys, time`), `utils/helpers.py:3-7` (`os, sys, math`) | Ruído; sinaliza código copiado sem revisão. |

---

## B) Construção da Skill

### Decisões de design

- **`SKILL.md` é o orquestrador (o "prompt"), `references/` é o conhecimento.**
  O `SKILL.md` descreve as 3 fases, as "golden rules" (detectar-nunca-assumir,
  todo finding com `file:line`, parada obrigatória na Fase 2, preservar contrato
  dos endpoints, validar de verdade) e aponta qual arquivo de referência ler em
  cada fase. Assim o corpo do prompt fica enxuto e o detalhe fica sob demanda.
- **5 arquivos de referência**, um por área de conhecimento exigida:
  `ProjectAnalyses.md` (heurísticas de detecção), `AntiPatternCatalog.md`
  (catálogo com sinais + severidade), `AuditReportTemplate.md` (formato exato dos
  blocos de saída das Fases 1/2/3), `ArchitecturalGuidelines.md` (regras das
  camadas MVC) e `RefactoringPlaybook.md` (transformações antes/depois).
- **Formato de saída padronizado** — os blocos `PHASE 1`, `ARCHITECTURE AUDIT
  REPORT` e `PHASE 3` são fixados no template para que o relatório seja idêntico
  em qualquer stack.

### Anti-patterns incluídos e por quê

O catálogo tem **14 anti-patterns** com severidade distribuída, escolhidos a
partir da análise manual (cada problema real dos 3 projetos mapeia para uma
entrada):

- **CRITICAL:** God File, Hardcoded Secrets, SQL Injection, Raw-query/Unauth Admin
  Endpoint, Weak Crypto — cobrem as falhas de segurança e arquitetura mais graves.
- **HIGH:** Fat Controller, Tight Coupling (sem DI), Shared Mutable Global State —
  violações fortes de MVC/SOLID.
- **MEDIUM:** N+1 Queries, Missing Validation, Duplicate Logic e **Deprecated API
  Usage** (check obrigatório) — manutenibilidade e performance.
- **LOW:** Presentation logic na camada de API, Naming/Magic numbers/Debug.

A entrada de **APIs deprecated** é obrigatória e cita equivalentes modernos
(`body-parser`→`express.json`, `datetime.utcnow()`→`datetime.now(timezone.utc)`,
`Query.get()`→`db.session.get()`, `flask.ext.*`→`flask_*`, `md5`→bcrypt/werkzeug).

O playbook tem **14 transformações** com exemplos de código **antes/depois** em
Python e Node — uma para cada anti-pattern.

### Como garanti que a skill é agnóstica de tecnologia

- **Detecção baseada em evidência**, nunca no nome do projeto: manifesto
  (`requirements.txt`/`package.json`), imports, drivers e strings de conexão.
- **Exemplos pareados Python/Flask e Node/Express** em todo o catálogo e playbook,
  mapeando cada conceito MVC ao idioma do framework (Blueprints vs Router).
- **A skill foi escrita uma vez e copiada byte-a-byte** para os 3 projetos — se
  dependesse de detalhes de um projeto, falharia nos outros. Foi validada nas duas
  linguagens e em dois níveis de organização (monolito puro × parcialmente
  organizado).

### Desafios encontrados

- **Projeto parcialmente organizado (task-manager).** A Fase 3 não podia
  "reconstruir do zero" — a guideline ganhou uma seção explícita de "adaptando a
  projetos já organizados": preservar o que está correto e corrigir os vazamentos
  (extrair controllers, centralizar overdue, trocar o hash).
- **Correções que alteram comportamento** (parar de retornar senha, hash real,
  remover `/admin/query`). A regra adotada: preservar o contrato dos endpoints,
  mas quando a correção de segurança muda o retorno, isso é declarado
  explicitamente no relatório.
- **Validação real, não presumida.** A Fase 3 exige subir a app (venv/npm) e
  bater nos endpoints com `curl` — o relatório só marca ✓ com evidência.

---

## C) Resultados

Skill executada nos três projetos. Relatórios completos em
[`reports/`](reports/). Os três atingem **todos os critérios de aceite
obrigatórios** (stack detectada, ≥5 findings, ≥1 CRITICAL/HIGH, app funcionando
após a refatoração).

### Resumo dos relatórios de auditoria

| Projeto | Stack detectada | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|-----------------|:--------:|:----:|:------:|:---:|:-----:|
| 1 · [code-smells-project](reports/audit-project-1.md) | Python 3 / Flask 3.1.1 / SQLite | 6 | 3 | 3 | 2 | **14** |
| 2 · [ecommerce-api-legacy](reports/audit-project-2.md) | Node.js / Express 4.18 / SQLite | 5 | 3 | 3 | 2 | **13** |
| 3 · [task-manager-api](reports/audit-project-3.md) | Python 3 / Flask 3.0 + SQLAlchemy / SQLite | 4 | 1 | 4 | 3 | **12** |

Detecção de **APIs deprecated** presente em todos: `sqlite3.verbose()` legado
(projeto 2), `datetime.utcnow()` + `Query.get()` (projeto 3), `debug=True`
hardcoded (projeto 1).

### Comparação antes/depois (estrutura)

**Projeto 1 — code-smells-project**
```
ANTES (monolito, 4 arquivos)        DEPOIS (MVC em src/)
app.py                              src/app.py                 (composition root)
controllers.py                      src/config/{settings,database}.py
models.py                           src/models/{produto,usuario,pedido}_model.py
database.py                         src/controllers/{produto,usuario,pedido,relatorio}_controller.py
                                    src/services/notification_service.py
                                    src/views/routes.py        (Blueprint fino)
                                    src/middlewares/error_handler.py
                                    app.py                     (boot → create_app)
```

**Projeto 2 — ecommerce-api-legacy**
```
ANTES (God class, 3 arquivos)       DEPOIS (MVC em src/)
src/app.js                          src/app.js                 (composition root)
src/AppManager.js  (God class)      src/config/{settings,database}.js
src/utils.js       (segredos+globals) src/models/{user,course,enrollment,payment,audit,report}Model.js
                                    src/services/{crypto,payment,cache}Service.js
                                    src/controllers/{checkout,report,user}Controller.js
                                    src/routes/{checkout,admin,user}Routes.js
                                    src/middlewares/{errorHandler,validateCheckout,validateUserId}.js
```

**Projeto 3 — task-manager-api** (já parcialmente organizado → melhorado)
```
ANTES                               DEPOIS
app.py (segredos + health)          config/settings.py           NOVO (segredos via env/dotenv)
models/ (senha exposta, MD5)        controllers/{task,user,report,category}_controller.py  NOVO
routes/ (rotas "gordas", N+1)       middlewares/error_handler.py NOVO (erros centralizados)
services/ (SMTP hardcoded)          models/  → hash werkzeug, sem senha no to_dict, overdue único
utils/                              routes/  → finas (request → controller → jsonify)
                                    app.py   → create_app() (composition root)
```

### Antes/depois — principais correções aplicadas

| Problema | Antes | Depois |
|----------|-------|--------|
| SQL Injection (P1) | `"... WHERE id = " + str(id)` | 100% queries parametrizadas (`execute(sql, (id,))`) |
| Segredos hardcoded (P1/P2/P3) | `SECRET_KEY`, `pk_live_...`, `senha123` no código | lidos de `os.getenv` / `process.env` |
| Hash de senha (P1/P2/P3) | texto puro / `badCrypto` / MD5 | werkzeug `pbkdf2:sha256` / `crypto.scrypt` |
| Senha na resposta (P1/P3) | `senha`/`password` retornados pela API | removidos da serialização |
| SQL arbitrário (P1) | `/admin/query` executa `request.sql` | endpoint removido (404) |
| N+1 (P1/P2/P3) | query por item em loop | JOIN único / `joinedload` / counts agrupados |
| God class/file (P1/P2) | tudo em 1 arquivo | separado em models/controllers/views |
| Estado global (P1/P2) | `db_connection` / `globalCache` globais | encapsulado em config/serviço |
| Integridade referencial (P2) | delete deixava órfãos | cascade limpa enrollments/payments |

### Checklist de validação (preenchido — 3/3 projetos)

| Item | P1 code-smells | P2 ecommerce | P3 task-manager |
|------|:---:|:---:|:---:|
| **Fase 1** — Linguagem detectada | ✅ | ✅ | ✅ |
| Framework detectado | ✅ Flask 3.1.1 | ✅ Express 4.18 | ✅ Flask 3.0 + SQLAlchemy |
| Domínio descrito | ✅ E-commerce | ✅ LMS/checkout | ✅ Task Manager |
| Nº de arquivos condiz | ✅ 4 | ✅ 3 | ✅ 15 |
| **Fase 2** — Segue o template | ✅ | ✅ | ✅ |
| Cada finding com arquivo:linha | ✅ | ✅ | ✅ |
| Ordenado por severidade | ✅ | ✅ | ✅ |
| ≥ 5 findings | ✅ 14 | ✅ 13 | ✅ 12 |
| Detecção de APIs deprecated | ✅ | ✅ | ✅ |
| Pausa/confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura MVC | ✅ | ✅ | ✅ |
| Config sem hardcoded | ✅ | ✅ | ✅ |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| **App inicia sem erros** | ✅ | ✅ | ✅ |
| **Endpoints originais respondem** | ✅ | ✅ | ✅ |

### Logs das aplicações rodando após a refatoração

Verificação independente (portas alternativas porque a 5000 está ocupada pelo
AirPlay Receiver do macOS):

```text
===== CODE-SMELLS (Flask, porta 5061) =====
GET /health   -> 200
GET /produtos -> 200

===== ECOMMERCE (Express, porta 3061) =====
GET /api/admin/financial-report -> 200
POST /api/checkout (card 4111…) -> {"msg":"Sucesso","enrollment_id":2,"status":"PAID"}

===== TASK-MANAGER (Flask+SQLAlchemy, porta 5062) =====
seed.py -> 3 usuários, 4 categorias, 10 tasks
GET /tasks -> 200
GET /users -> 200  (sem campo password → vazamento corrigido)
```

### Como a skill se comportou em stacks diferentes

- **Monolito Python puro (P1):** reestruturação completa de 4 arquivos para MVC
  em `src/`; o maior volume de correções de segurança (SQLi, `/admin/query`).
- **God class Node (P2):** dissolveu uma classe única em models/controllers/
  routes/services; trocou callback-hell por camadas e o driver legado por acesso
  promisificado.
- **Flask parcialmente organizado (P3):** a skill **não** reconstruiu do zero —
  preservou `models/`, `routes/`, `services/` e adicionou a camada `controllers/`
  + `config/` + `middlewares/`, centralizou a lógica de overdue duplicada e
  eliminou os N+1 com `joinedload`.

> **Nota sobre mudanças de comportamento:** correções de segurança que alteram o
> retorno da API foram **intencionais e documentadas** nos relatórios — parar de
> devolver a senha, aplicar hash real, remover o endpoint de SQL arbitrário e
> fazer o `DELETE` limpar registros órfãos. O contrato dos demais endpoints
> (paths, métodos e formato de resposta) foi preservado.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- **Python 3.9+** (projetos 1 e 3) e **Node.js 18+** (projeto 2).

### Executar a skill em cada projeto

A skill já está em `.claude/skills/refactor-arch/` dentro dos três projetos.
Invoque com o slash command `/refactor-arch`:

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy (Node/Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask)
cd ../task-manager-api
claude "/refactor-arch"
```

A Fase 1 imprime o resumo do stack; a Fase 2 imprime o relatório de auditoria e
**pausa pedindo confirmação** (`[y/n]`); ao responder `y`, a Fase 3 refatora e
valida.

### Validar que a refatoração funcionou

**Projeto 1 — code-smells-project**
```bash
cd code-smells-project
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py          # sobe em http://localhost:5000
# noutro terminal:
curl localhost:5000/health
curl localhost:5000/produtos
```

**Projeto 2 — ecommerce-api-legacy**
```bash
cd ecommerce-api-legacy
npm install
npm start                        # sobe em http://localhost:3000
# noutro terminal (ver api.http):
curl -X POST localhost:3000/api/checkout -H 'Content-Type: application/json' \
  -d '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}'
curl localhost:3000/api/admin/financial-report
```

**Projeto 3 — task-manager-api**
```bash
cd task-manager-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py         # popula tasks.db (rode antes do 1º boot)
.venv/bin/python app.py          # sobe em http://localhost:5000
# noutro terminal:
curl localhost:5000/tasks
curl localhost:5000/reports/summary
```

Refatoração bem-sucedida = a aplicação sobe sem erros e todos os endpoints
originais continuam respondendo (com as correções de segurança aplicadas).
