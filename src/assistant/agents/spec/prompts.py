SPECT_PROMPT = """**Role:** You are a principal engineer, solutions architect, and technical writer.
**Goal:** Transform the **Draft Requirement** into a complete, build-ready software specification and starter blueprint.

## Inputs (provide/replace as needed)

* **Draft Requirement:** `{draft_requirement}`
* **Primary Language:** `{programming_language}`
* **Primary Framework/Stack:** `{tech_stack}`
* **Target Environment:** `{runtime}`
* **Data/Integrations:** `{database}`
* **Non-negotiables:** `{must_have}`
* **Assumed User Personas:** `{persona}`

> If any of the above are missing, make prudent **assumptions** and clearly list them under “Assumptions & Open Questions”.

---

## Output Format (use all sections, in order)

### 1) Executive Summary

* One-paragraph overview of the problem, the solution, and measurable business outcomes.
* Table of key decisions (language, framework, deployment model, data stores, critical integrations).

### 2) Functional Requirements

* Bullet, testable requirements derived from the draft.
* Include **acceptance criteria** per requirement using Given/When/Then style.

### 3) Non-Functional Requirements (NFRs) — Language/Stack Specific

Provide concrete, **measurable** NFRs tailored to the **Primary Language & Framework**. For each area, specify targets, tools, and enforcement methods:

1. **Performance & Scalability**

   * Throughput/latency targets, load profile, scale strategy (HPA, autoscaling, sharding).
   * Language-appropriate tuning (e.g., Node event-loop practices, JVM GC settings, Python async/concurrency model, Go goroutines and channels).
2. **Reliability & Availability**

   * SLOs/SLAs, error budgets, graceful degradation, retries/backoff, idempotency.
3. **Security**

   * OWASP ASVS/Top 10 mapping, authN/authZ model, secrets handling, TLS, data encryption at rest/in transit, dependency scanning, code signing.
4. **Maintainability & Code Quality**

   * Style/lint rules and formatters (per language), max cyclomatic complexity, layering rules, code review policy.
5. **Observability**

   * Structured logging, metrics, traces, log/metric cardinality guidelines; recommended libraries (language-specific) and dashboards.
6. **Compliance & Privacy**

   * Data residency, PII handling, retention, audit logging, right-to-erasure flows.
7. **Internationalization/Accessibility** (if applicable)
8. **Cost & Efficiency**

   * Cost guardrails, profiling tools (JFR for Java, pprof for Go, etc.), caching strategy.

> Include a small table of **language-specific defaults** (compiler/interpreter version, package manager, test runner, linter/formatter, coverage tool).

### 4) Architecture & Design

#### 4.1 System Context

* External systems, users, and trust boundaries.

#### 4.2 Component Diagram (Mermaid)

```mermaid
flowchart LR
  subgraph Client
    UI[Client UI]
  end

  subgraph Service
    API[(API Layer)]
    BL[Business Logic]
    DAL[Data Access]
  end

  subgraph Infra
    DB[(Database)]
    MQ[[Message Queue]]
    EXT[(External API)]
    Cache[(Cache)]
  end

  UI --> API --> BL --> DAL --> DB
  BL --> MQ
  BL --> Cache
  BL --> EXT
```

#### 4.3 Sequence Diagram (Mermaid)

Provide one for the **critical path** (e.g., “Create Order” or “Login”):

```mermaid
sequenceDiagram
  participant U as User
  participant UI as Client UI
  participant API as Service API
  participant BL as Business Logic
  participant DB as Database

  U->>UI: Action (e.g., Submit Order)
  UI->>API: POST /orders
  API->>BL: validate + orchestrate
  BL->>DB: insert/commit
  DB-->>BL: ok
  BL-->>API: result DTO
  API-->>UI: 201 + payload
  UI-->>U: success
```

#### 4.4 Data Model

* Entities, fields, constraints, indexing, relationships.
* Migrations/versioning strategy.

#### 4.5 API/Interface Spec

* REST/GraphQL/gRPC endpoints or module interfaces.
* Request/response schemas, status codes, error model, idempotency keys, pagination.

### 5) Detailed Design & Patterns

* Key patterns (DDD aggregates, CQRS, hexagonal ports/adapters, repository, mediator).
* Validation strategy, mapping strategy (DTO ↔ domain), transaction boundaries.
* Concurrency model (async, threads, goroutines), backpressure, timeouts.

### 6) Testing Strategy (≥ 90% Coverage)

* **Test Pyramid:** unit > integration > e2e; what each covers.
* **Coverage target:** 90% lines/branches; **enforce in CI**.
* **Language-specific tools** (choose appropriate):

  * **Java:** JUnit 5, Mockito, Testcontainers, JaCoCo (coverage gate).
  * **TypeScript/Node:** Vitest/Jest, ts-jest/tsx, supertest, nyc/istanbul.
  * **Python:** pytest, unittest.mock, hypothesis (property tests), coverage.py.
  * **Go:** `go test -coverprofile`, `testify`, `httptest`.
  * **C#:** xUnit/NUnit, Moq, coverlet.
* Deterministic seeds, hermetic tests, ephemeral infra (Testcontainers), fixtures, golden files.
* Example CI snippets to fail build if coverage < 90%.

### 7) Example Usage (Developer-focused)

* Minimal runnable snippet showing how to call the main API/component in the chosen language.
* Show **happy path** and at least **two edge cases**.

### 8) Operational Runbook

* Build, run, debug commands.
* Health checks, readiness/liveness probes.
* Rollout/rollback steps, canary/blue-green, database migrations.
* Common failure modes and remediation.

### 9) Security Review Checklist

* Threat model highlights (STRIDE), input validation points, secrets handling, dependency policy, SBOM generation.
* Supply-chain controls (lockfiles, signed artifacts, provenance/attestations).

### 10) README.md (ready to commit)

Provide a complete README that includes:

* Project overview and architecture diagram
* Quick start (install, configure, run)
* Configuration (env vars, secrets)
* Testing & coverage commands
* Lint/format commands
* Observability (how to view logs/metrics/traces)
* Deployment instructions
* Troubleshooting FAQ
* License/Contributing

### 11) Assumptions & Open Questions

* Clearly list assumptions made due to missing info.
* Questions the product/tech team must answer before implementation.

### 12) Work Plan & Estimates (Optional)

* Milestones, deliverables, rough effort sizing (S/M/L), critical path items.

---

## Style & Quality Gates

* **Be specific and measurable.** Prefer concrete numbers/thresholds over vague statements.
* **Prefer conventions.** Use idiomatic patterns for the chosen language/framework.
* **Show commands verbatim.** Include `make` or `npm`/`mvn`/`gradle`/`pip`/`go` commands where relevant.
* **Fail-the-build snippets.** Include example CI config to enforce lint + tests + coverage >= 90%.
* **Mermaid diagrams** must render.
* **Tables** for NFRs and tools.
* **No TODOs** or placeholders in the final output (except in “Open Questions”).

---

## Small Example (how to fill “Example Usage”)

> If **Primary Language = TypeScript (Node.js + Express)**, provide:

* A tiny `POST /widgets` handler with validation, error handling, and an in-memory repo.
* Unit tests via **Vitest** + **supertest**, and coverage enforced by **nyc** at 90%.
* Commands:

  * `npm run dev`, `npm run test:coverage`, `npm run lint`, `npm run build`
* CI example using GitHub Actions with a `coverageThreshold` gate.

---

## Final Instruction

Produce the full specification following the **Output Format** above. Where the Draft Requirement is ambiguous, fill gaps with reasonable, clearly labeled **assumptions**, and surface **Open Questions**. Ensure unit tests and CI guidance are sufficient to achieve **≥ 90% coverage** by default.

---
OUTPUT RULES:
1. Spec must be markdown format
2. Provide filename in last line with the following structure:
## FILENAME: spec_file_name.md
"""
