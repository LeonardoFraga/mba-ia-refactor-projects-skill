# ProjectAnalyses

Este documento guia a Fase 1 da skill: analisar o projeto e identificar linguagem, framework, arquitetura, domínio e dependências.

## Detecção de linguagem
- Extensões de arquivo:
  - `.py` → Python
  - `.js`, `.mjs`, `.cjs` → JavaScript/Node.js
  - `.ts` → TypeScript
- Arquivos de manifesto:
  - `requirements.txt`, `Pipfile`, `pyproject.toml` → Python
  - `package.json` → Node.js
- Shebangs e comentários init:
  - `#!/usr/bin/env python` em scripts Python.
  - `import`, `from` no topo de arquivos indica Python.
  - `const`, `require`, `module.exports`, `import` no topo indica Node.js.

## Detecção de framework
- Python/Flask:
  - Presença de `from flask import`, `Flask(`, `app.route(`, `flask_cors`, `flask_sqlalchemy`.
  - `app = Flask(__name__)` ou `Blueprint`.
- Python/Django:
  - `django.shortcuts`, `models.py` com `django.db.models`, configurações `settings.py` e `urls.py`.
- Node/Express:
  - `require('express')`, `import express from 'express'`, `app.use(express.json())`, `app.listen(`.
  - `router = express.Router()` e `module.exports = router`.
- Outros frameworks:
  - `fastapi`, `starlette`, `koa`, `hapi`, `sails` — use sinal específico de importação.

## Detecção de banco de dados e persistência
- Drivers e ORMs comuns:
  - SQL: `sqlite3`, `psycopg2`, `pymysql`, `sqlalchemy`, `knex`, `pg`, `mysql`, `mysql2`.
  - NoSQL: `pymongo`, `mongodb`, `mongoose`, `redis`, `cassandra`.
  - ORM/ODM: `flask_sqlalchemy`, `sqlalchemy.orm`, `peewee`, `mongoose`.
- Strings de conexão e comandos SQL:
  - `sqlite:///`, `postgres://`, `mysql://`, `mongodb://`.
  - `SELECT`, `INSERT`, `UPDATE`, `DELETE` em literais de string.
- Arquivos de configuração e migração indicam persistência: `alembic`, `migrations`, `models.py`.

## Mapeamento de arquitetura
- Monoarquivo / monolítica:
  - Um único arquivo contém inicialização, rotas, lógica e acesso a dados.
  - Exemplo: `app.py` com rotas e queries inline.
- Separação parcial:
  - Projeto já tem `models/`, `routes/`, `services/` ou `controllers/`.
  - Se houver lógica distribuída, verifique se responsabilidades estão corretamente separadas.
- MVC organizado:
  - `app.py` ou `server.js` apenas inicializa a aplicação.
  - Rotas, controllers e models estão em diretórios distintos.
- Anti-patterns de arquitetura:
  - Controllers que importam modelos e também query executam persistência diretamente.
  - Models que importam objetos HTTP ou definem roteamento.

## Domínio do projeto
- Extraia o domínio por análise de nomes e rotas:
  - Nomes comuns: `user`, `task`, `product`, `pedido`, `checkout`, `order`, `cart`.
  - Rotas REST: `/users`, `/tasks`, `/products`, `/orders`, `/checkout`.
  - Mensagens de log ou variáveis: `Task Manager`, `E-commerce`, `LMS`, `checkout`.
- Responda as seguintes perguntas para o resumo de análise:
  - Qual é o domínio principal (por exemplo, Task Manager, E-commerce, LMS)?
  - Quais entidades centrais aparecem no código?
  - Qual tipo de arquitetura atual é detectado?

## Métricas de análise
- Contagem de arquivos de origem e diretórios.
- Linhas de código por arquivo e por camada.
- Sinais de acoplamento entre arquivos (imports recíprocos, `from routes import` em modelos, etc.).
- Dependências detectadas no manifesto.

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
- Dependências principais
- Domínio de negócio
- Arquitetura atual
- Diretórios e arquivos analisados
