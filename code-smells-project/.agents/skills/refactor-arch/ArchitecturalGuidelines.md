# ArchitecturalGuidelines

Este documento descreve as responsabilidades do padrão MVC alvo para backends Python/Flask e Node.js/Express. Ele orienta a Fase 3 da skill para que o refatoramento preserve a separação de camadas e gere uma arquitetura consistente.

## Visão geral do MVC
A arquitetura MVC para backends deve organizar o código em três camadas:

- **Models:** responsável por persistência, esquemas de dados e regras de domínio puras.
- **Controllers:** responsável por orquestrar fluxo, validar dados e aplicar a lógica de negócio usando models/services.
- **Views/Routes:** responsável por declarar endpoints HTTP, mapear requests/params e retornar respostas HTTP.

### Estrutura mínima sugerida
- `app.py` / `server.js` — composição de dependências e inicialização do aplicativo.
- `models/` — classes, funções de acesso a dados e abstrações de banco.
- `controllers/` — funções ou classes que recebem dados do request e coordenam a execução.
- `routes/` ou `views/` — definição de rotas/endpoints e ligação com controllers.
- `middlewares/` — validação, tratamento de erros e cross-cutting concerns.
- `config/` — configuração e variáveis de ambiente.

## Regras para Models
- Devem conter apenas lógica de dados e regras de domínio.
- Devem expor métodos de persistência e consulta (`find`, `create`, `update`, `delete`).
- Nunca devem acessar o objeto HTTP (`request`, `req`, `res`) ou montar respostas.
- Devem ser independentes da camada de roteamento.
- Devem dar preferência a operações compartilhadas e reutilizáveis sobre lógica duplicada.

## Regras para Controllers
- Devem ser a ponte entre rotas e modelos/services.
- Devem validar e sanitizar entrada antes de invocar a camada de domínio.
- Devem executar apenas a lógica de orquestração e tratamento de exceções.
- Devem retornar valores em formato neutro (JSON serializable, DTOs) e deixar a camada de rota criar a resposta HTTP.
- Devem ser testáveis isoladamente, sem dependência direta do framework HTTP.

## Regras para Views / Routes
- Devem declarar endpoints, métodos HTTP e parâmetros de rota.
- Devem mapear `request.params`, `request.query` e `request.body` para chamadas de controller.
- Devem lidar com códigos de status HTTP e transformar o retorno do controller em resposta.
- Devem ser finas; não devem conter lógica de negócio, validações complexas ou consultas ao banco.

## Regras de composição e configuração
- A inicialização do app deve ser concentrada em um único módulo raiz.
- Variáveis de ambiente, strings de conexão e segredos devem viver em `config/` ou no ambiente, nunca hardcoded.
- Middlewares devem ser reutilizáveis e independentes da lógica de negócio.
- A camada de rotas deve importar controllers, não models diretamente.
- Services são permitidos como camada opcional entre controller e model para domínios complexos.

## Padrões de design desejados
- **Injeção de dependência:** passe repositórios, clientes e configurações via funções ou construtores.
- **Single Responsibility Principle:** cada arquivo e função tem uma razão única para mudar.
- **Separation of Concerns:** mantenha validação, persistência, roteamento e apresentação em camadas distintas.

## Exemplos de estrutura de importação
- Python/Flask:
  - `routes.py` importa `controllers/*.py`
  - `controllers/*.py` importa `models/*.py` ou `services/*.py`
  - `models/*.py` não importa `routes` ou `controllers`

- Node/Express:
  - `routes/*.js` importa `controllers/*.js`
  - `controllers/*.js` importa `models/*.js` ou `services/*.js`
  - `models/*.js` não importa rotas ou aplicação HTTP

## Validando a arquitetura
Ao refatorar, confirme que:
- Endpoints originais continuam atendendo os mesmos paths e métodos.
- Não há consultas SQL/NoSQL diretas nas definições de rota.
- Não há `request`/`req`/`res` dentro de modelos.
- Configurações sensíveis não estão definidas em código-fonte.
