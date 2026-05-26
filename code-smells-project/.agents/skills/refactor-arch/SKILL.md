---
name: refactor-arch
description: "Use when: refactoring architecture, auditing code structure, improving project layout"
sources:
  - ProjectAnalyses.md
  - AntiPatternCatalog.md
  - AuditReportTemplate.md
  - ArchitecturalGuidelines.md
  - RefactoringPlaybook.md
  - ExtensionGuide.md
---

## Overview

This skill analyzes backend projects, generates an architecture audit report, and refactors legacy code toward MVC. Use the attached reference documents to perform:

1. **Phase 1 — project analysis and stack detection**
2. **Phase 2 — anti-pattern detection and report generation**
3. **Phase 3 — refactoring to MVC with validation**

## Language Support

### Tier 1: Full Support (detection + refactoring examples)
- ✅ Python/Flask
- ✅ Node.js/Express
- ✅ Java/Spring Boot
- ✅ C#/.NET/ASP.NET Core

### Tier 2: Principles Only (detection, no concrete examples)
- ⚠️ Go, Rust, Kotlin, PHP, Ruby, and others

Tier 2 languages can use generic anti-patterns and MVC principles, but Phase 3 refactoring requires manual adaptation.

See `ExtensionGuide.md` for how to add support for new languages.

## Methodology: Principles-Agnostic, Implementation-Specific

The skill is **agnostic of principles** (language-agnostic in concepts) but **specific in implementation** (framework/pattern-specific). This means:

- **Generic:** Anti-patterns like God Class, Fat Controller, Hardcoded Secrets exist in any language
- **Generic:** MVC separation (Models/Controllers/Views) applies universally
- **Specific:** Framework detection (Flask vs FastAPI vs Spring Boot) requires explicit knowledge
- **Specific:** Refactoring transformations need language/framework examples
