# ExtensionGuide

Este documento descreve como estender a skill `refactor-arch` para novas linguagens e frameworks.

## Arquitetura da skill

A skill é estruturada em **camadas de conhecimento**:

```
┌─────────────────────────────────────────────┐
│ SKILL.md (Orchestrator)                     │
│ - Coordena 3 fases de execução              │
│ - Lê referencias conforme necessário        │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┬──────────────┬──────────────┐
    │                     │              │              │
    ▼                     ▼              ▼              ▼
ProjectAnalyses      AntiPatternCatalog  Architectural  RefactoringPlaybook
(Fase 1)             (Fase 2)            Guidelines     (Fase 3)
                                         (Todas)
```

## Tier de suporte

### Tier 1: Suporte Completo (+ exemplos de refatoração)
- Python/Flask
- Node.js/Express 
- Java/Spring Boot
- C#/.NET/ASP.NET Core

Essas linguagens têm:
- Detecção de framework em `ProjectAnalyses.md`
- Padrões de arquitetura esperados
- Exemplos antes/depois em `RefactoringPlaybook.md`

### Tier 2: Princípios Aplicáveis (sem exemplos)
- Go, Rust, Kotlin, PHP, Ruby, Scala, Clojure, etc.

Essas linguagens:
- Podem usar os anti-patterns genéricos (Fase 2)
- Podem usar as regras MVC genéricas (ArchitecturalGuidelines)
- Requerem adaptação manual para refatoração (Fase 3)
- Não têm exemplos específicos em `RefactoringPlaybook`

---

## Como adicionar suporte para uma nova linguagem (Tier 1)

### Exemplo: Adicionar suporte para Go

#### 1. Expandir `ProjectAnalyses.md`

Adicione uma seção **"Go / standard library + frameworks"**:

```markdown
### Go / Web Frameworks

#### Sinais de Go:
- Extensões: `.go`
- Manifesto: `go.mod`, `go.sum`
- Estrutura: package main com func main()
- Imports típicos: `import "net/http"`, `import "github.com/gin-gonic/gin"`

#### Frameworks comuns:
- **Gin**: `import "github.com/gin-gonic/gin"`, `gin.New()`, `router.GET()`
- **Echo**: `import "github.com/labstack/echo"`, `e := echo.New()`
- **Chi**: `import "github.com/go-chi/chi"`, `r := chi.NewRouter()`

#### Banco de dados:
- SQL: `database/sql`, `github.com/lib/pq`, `github.com/go-sql-driver/mysql`
- ORM: `gorm.io/gorm`, `entgo.io/ent`
- NoSQL: `go.mongodb.org/mongo-driver`

#### Estrutura MVC esperada (Gin):
```
cmd/server/main.go      # Raiz
internal/config/config.go  # Configuração
internal/models/user.go    # Models
internal/handlers/user.go  # Handlers/Controllers
internal/routes/routes.go  # Rotas
internal/db/db.go          # Database setup
```

#### Anti-patterns Go comuns:
- `var GlobalDB *sql.DB` (estado global)
- Handlers com SQL direto: `func GetUser(c *gin.Context) { rows := db.Query(...) }`
- Secrets em `main.go`: `const apiKey = "secret123"`
- Valores hardcoded em structs de configuração
```

#### 2. Adicionar exemplos em `RefactoringPlaybook.md`

Para cada anti-pattern, adicione uma seção Go:

```markdown
### Go / Gin

**Antes:**
\`\`\`go
func GetUser(c *gin.Context) {
  id := c.Param("id")
  rows, _ := db.Query("SELECT * FROM users WHERE id = " + id)
  // ... transformar rows em JSON
}
\`\`\`

**Depois:**
\`\`\`go
// handlers/user_handler.go
package handlers

func GetUser(c *gin.Context) {
  user, err := service.GetUserByID(c.Param("id"))\n  if err != nil {
    c.JSON(400, gin.H{"error": err.Error()})\n    return\n  }\n  c.JSON(200, user)\n}
\`\`\`
```

#### 3. Atualizar `ArchitecturalGuidelines.md`

Adicione uma seção Go:

```markdown
## Go / Gin

### Estrutura de imports esperada:
- `cmd/server/main.go` inicializa e compõe tudo
- `internal/handlers/` importa de `internal/services/`
- `internal/services/` importa de `internal/models/`
- `internal/models/` não importa nada do framework

### Padrões de design:
- **Dependency Injection**: passar `*sql.DB` ou `*gorm.DB` para handlers via constructores
- **Interfaces**: definir interfaces de repositório para facilitar testes
- **Middlewares**: usar `gin.HandlerFunc` para validação e tratamento de erros
```

#### 4. Testar em um projeto real

Crie um projeto Go de teste ou encontre um legado para validar:

```bash
cd ../go-example-project
claude "/refactor-arch"
```

Verifique que:
- Fase 1 detecta corretamente Go e Gin
- Fase 2 encontra >= 5 anti-patterns
- Fase 3 refatora para a estrutura esperada

---

## Como adicionar suporte Tier 2 (apenas princípios)

Se você quer suportar uma linguagem mas **não quer criar exemplos completos de refatoração**:

1. **Apenas atualize `ProjectAnalyses.md`** com sinais de detecção
2. **Os anti-patterns de Fase 2 continuam genéricos** (God Class, Fat Controller, etc.)
3. **Fase 3 requer edição manual** ou adaptação case-by-case

Exemplo:

```markdown
### Rust / Actix-web

#### Sinais de Rust:
- Extensões: `.rs`
- Manifesto: `Cargo.toml` com `name = "actix-web"`
- `fn main()` com `actix_web::main`
- Imports: `use actix_web::{web, App, HttpServer}`

Estrutura MVC esperada segue padrão similar, mas com particularidades de Rust (lifetimes, ownership, etc.).
```

---

## Checklist de extensão

Para adicionar uma nova linguagem a Tier 1:

- [ ] Adicionar seção em `ProjectAnalyses.md` (detecção de framework e banco)
- [ ] Adicionar exemplos antes/depois em `RefactoringPlaybook.md` (mínimo 3-4 anti-patterns)
- [ ] Adicionar convenções e regras em `ArchitecturalGuidelines.md`
- [ ] Testar em um projeto real de referência
- [ ] Validar Fases 1, 2, 3 funcionam corretamente
- [ ] Documentar resultado no README

---

## Limitações conhecidas

### Por design
- Anti-patterns genéricos podem não detectar idiomas específicos de uma linguagem (ex: Go goroutines)
- Refatoração (Fase 3) requer conhecimento profundo do ecossistema da linguagem
- Algumas linguagens (ex: Rust) têm paradigmas que não se encaixam em MVC simples

### Recomendações
- Se uma linguagem tem um padrão dominante diferente de MVC (ex: event-driven em Elixir), considere documentar como adaptações necessárias
- Teste sempre em 2-3 projetos reais antes de marcar como "suportada"
- Mantenha comentários nos exemplos explicando idiomas específicos

