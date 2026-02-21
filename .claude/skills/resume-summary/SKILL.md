---
name: resume-summary
description: Analyze a codebase and generate structured resume-ready notes. Use this skill whenever the user wants to document a project for their resume, extract resume bullet points from code, summarize a codebase for job applications, or prepare portfolio notes. Trigger on phrases like "resume notes", "resume bullets", "portfolio summary", "document this project for my resume", "what should I put on my resume about this", "help me describe this project", or any request to translate a codebase into professional accomplishments. Also trigger when the user asks to "analyze this repo for my resume" or "what's impressive about this codebase".
---

# Resume Notes Generator

Analyze a codebase and produce a structured markdown document with resume-ready notes. The user is a senior-level engineer (backend, full-stack, AI/ML) and the sole developer of the project. The output should make them look like a strong, thoughtful, senior engineer who ships production-quality software.

## How to approach the analysis

Think like a hiring manager or senior engineering interviewer reading a resume. They care about:

- **Impact and scale** — numbers, metrics, performance characteristics
- **Technical depth** — sophisticated patterns, not just "used React"
- **Architectural judgment** — why decisions were made, not just what was built
- **Breadth of ownership** — infra, backend, frontend, DevOps, testing, CI/CD

Your job is to dig through the codebase and surface the things that would make an interviewer say "tell me more about that."

## Step-by-step process

### 1. Reconnaissance

Start by getting the lay of the land. Run these in sequence:

```bash
# Top-level structure
find . -maxdepth 2 -type f | head -100
ls -la

# Package/dependency files (reveals tech stack)
cat package.json 2>/dev/null || cat requirements.txt 2>/dev/null || cat Cargo.toml 2>/dev/null || cat go.mod 2>/dev/null || cat Gemfile 2>/dev/null || cat pom.xml 2>/dev/null || echo "No standard package file found"

# Docker / infra
cat docker-compose.yml 2>/dev/null || cat Dockerfile 2>/dev/null || echo "No Docker config"
ls -la .github/workflows/ 2>/dev/null || ls -la .gitlab-ci* 2>/dev/null || echo "No CI config found"

# README for context
cat README.md 2>/dev/null || cat README.rst 2>/dev/null || echo "No README"

# Git stats for scale metrics
git log --oneline | wc -l 2>/dev/null  # total commits
git log --format='%H' | wc -l 2>/dev/null
find . -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' | head -200 | xargs wc -l 2>/dev/null | tail -1  # rough LOC
```

### 2. Deep dive into architecture

Now explore the core of the application. Read key files to understand:

- **Entry points** — main files, app initialization, server setup
- **Data models** — database schemas, ORM models, type definitions
- **API surface** — routes, controllers, GraphQL schemas, RPC definitions
- **Core business logic** — the "interesting" modules, services, algorithms
- **Infrastructure** — caching layers, queue systems, auth, middleware
- **Testing** — test structure, coverage config, test utilities
- **Configuration** — env handling, feature flags, multi-environment support

For each area, read the actual source files. Don't guess from filenames alone — open them and understand what's happening.

### 3. Hunt for impressive details

These are the things that separate a senior engineer's project from a junior's. Actively look for:

- **Performance optimizations** — caching strategies, query optimization, lazy loading, connection pooling, batch processing, pagination strategies
- **Scalability patterns** — message queues, worker pools, microservice boundaries, rate limiting, circuit breakers
- **Security measures** — auth/authz patterns, input validation, CSRF/XSS protection, secrets management, encryption
- **Error handling** — graceful degradation, retry logic, dead letter queues, structured logging, monitoring hooks
- **Testing sophistication** — integration tests, fixtures, mocking strategies, test isolation, CI pipelines
- **DevOps maturity** — Docker configs, CI/CD pipelines, deployment strategies, infrastructure as code, environment management
- **AI/ML specifics** — model serving, prompt engineering patterns, RAG pipelines, fine-tuning setups, evaluation frameworks, vector stores, embedding strategies
- **Data engineering** — ETL pipelines, data validation, migration strategies, backup approaches
- **API design quality** — versioning, pagination, error responses, documentation, OpenAPI specs

### 4. Extract metrics where possible

Scan for concrete numbers to quantify the project. Look for:

```bash
# Number of API endpoints
grep -r "router\.\|@app\.\|@router\.\|app\.get\|app\.post\|app\.put\|app\.delete\|@Get\|@Post\|@Put\|@Delete" --include="*.py" --include="*.ts" --include="*.js" --include="*.java" -l | wc -l

# Number of database models/tables
grep -r "class.*Model\|CREATE TABLE\|Schema({" --include="*.py" --include="*.ts" --include="*.js" --include="*.sql" -l | wc -l

# Number of test files
find . -name '*test*' -o -name '*spec*' | grep -v node_modules | grep -v __pycache__ | wc -l

# Lines of code by language (rough)
find . -name '*.py' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' | xargs wc -l 2>/dev/null | tail -1
find . -name '*.ts' -o -name '*.tsx' | grep -v node_modules | xargs wc -l 2>/dev/null | tail -1
find . -name '*.js' -o -name '*.jsx' | grep -v node_modules | xargs wc -l 2>/dev/null | tail -1
```

Also look inside the code for clues about scale: pagination limits, batch sizes, rate limit values, cache TTLs, pool sizes — these suggest the kind of load the system is designed for.

## Output format

Write the output as a clean markdown file saved to the current directory as `resume-notes.md`. Use this structure:

```markdown
# Resume Notes: [Project Name]

_Generated [date] — these are raw notes for resume crafting, not a final resume._

## Project Overview

[2-3 paragraph summary of what the project is, what problem it solves, and who it's for. Write this in a way that a non-technical recruiter could understand the first paragraph, but a technical interviewer would appreciate the depth in the rest.]

## Tech Stack

| Layer             | Technologies |
| ----------------- | ------------ |
| Language(s)       | ...          |
| Backend Framework | ...          |
| Frontend          | ...          |
| Database          | ...          |
| Caching           | ...          |
| Message Queue     | ...          |
| AI/ML             | ...          |
| Infrastructure    | ...          |
| CI/CD             | ...          |
| Testing           | ...          |
| Other Notable     | ...          |

_Only include rows that apply. Add rows for any additional categories discovered._

## System Architecture

[Describe the high-level architecture: how components interact, data flow, key design decisions and their rationale. Use plain language but be technically precise. If it's a monolith, describe the internal module structure. If it's microservices, describe the service boundaries and communication patterns.]

## Resume Bullet Points

These are written in strong action-verb format ready to adapt for a resume. Each one follows the pattern: **[Action verb] + [what you built/did] + [technical detail] + [impact/scale if available]**.

### Architecture & Design

- ...
- ...

### Core Features & Implementation

- ...
- ...

### Performance & Scalability

- ...

### Security & Reliability

- ...

### Testing & Quality

- ...

### DevOps & Infrastructure

- ...

### AI/ML (if applicable)

- ...

_Only include sections that have substantive bullets. Aim for 8-15 bullets total — quality over quantity._

## Noteworthy Implementation Details

[This section is for the "tell me about a technical challenge" interview questions. Describe 2-4 of the most interesting or complex things in the codebase — things that required real engineering judgment. For each one, explain the problem, the approach taken, and why it's a good solution. These should be things you'd be proud to talk about in an interview.]

## Suggested Resume Summary Line

[One punchy line that could go at the top of a resume describing this project. Two versions: one for a general engineering role, one for a specialized role matching the project's domain.]
```

## Important guidelines

- **Be specific, not generic.** "Implemented caching" is weak. "Implemented Redis-based response caching with TTL-based invalidation, reducing average API latency by serving cached results for repeated queries" is strong. Always tie back to the actual code you've read.
- **Don't invent metrics.** If you can measure or infer something from the code, great. If not, describe the capability qualitatively. Never fabricate numbers.
- **Frame everything as accomplishments.** The user built this — phrase things in a way that highlights their engineering skill and judgment, not just what the code does.
- **Assume senior-level audience.** Use proper technical terminology. Don't oversimplify for the bullet points — the recruiter reads the summary, the interviewer reads the bullets.
- **Be honest.** If the project is small, don't try to make it sound like it serves millions of users. Focus on the technical quality and thoughtfulness instead. A well-architected small project is more impressive than a messy large one.
- **Tailor to relevant roles.** The user works across backend, full-stack, AI/ML, and senior engineering roles. Emphasize accomplishments that resonate with these positions: system design, API architecture, data pipelines, ML infrastructure, and technical leadership signals.
