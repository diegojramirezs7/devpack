---
name: create-system-design
description: Create a high-level system design for a new project. Use this skill whenever the user wants to plan how a system should be structured before implementation — including architecture, data model, API design, frontend structure, and key technical decisions. Trigger on phrases like "system design", "architect this", "plan the system", "how should I structure this", "design the backend/frontend", "technical design", "project architecture", or any request to map out how components of a new app or system fit together. Also use when the user has a feature spec or product description and wants to turn it into a buildable technical plan. Even if the user just says "let's build X" or "let's make Y", if no design exists yet, trigger this skill to establish the technical foundation first.
---

# System Design

Create a high-level, tech-agnostic system design document that gives a team enough structure to start building — while staying loose enough to adapt as implementation reveals new information.

## Workflow

The process has two phases: a short interview to fill in gaps, then a draft that the user can iterate on.

### Phase 1: Quick Interview (3–5 questions max)

Before producing any design, ask targeted questions to understand the project. Don't ask about things that are already clear from context. Focus on unknowns that would significantly change the design.

Good questions to consider (pick only the ones that matter for this project):

- What's the core user flow? (What does a user actually do, step by step?)
- Who are the different types of users/roles?
- What are the most important data entities and how do they relate?
- Are there any integrations with external services (payments, auth providers, APIs)?
- What's the expected scale? (Handful of users? Thousands? Millions?)
- Is there a real-time component (live updates, collaboration, chat)?
- Are there any hard constraints? (Must run on-prem, must be mobile-first, must use a specific DB, etc.)
- Is this a greenfield project or does it need to integrate with existing systems?

Keep it conversational. Ask 3–5 questions in a single message. Don't overwhelm the user. If the user has already provided a feature spec or detailed description, you may have enough to skip straight to Phase 2.

### Phase 2: Produce the Design Document

Generate a markdown document with the sections below. The document should be:

- **Concrete enough** to start implementation from — someone should be able to read it and begin building
- **Loose enough** that it doesn't over-specify things that will change — avoid dictating exact file structures, class hierarchies, or implementation patterns unless the user asks
- **Tech-agnostic** by default — describe what's needed, not which framework to use, unless the user has specified their stack or asks for a recommendation
- **Readable by a developer** — no fluff, no corporate language, just clear technical communication

## Design Document Structure

Use this structure for the output document. Every section is required unless genuinely not applicable (e.g., no frontend for a pure API project). If a section doesn't apply, omit it — don't include it with "N/A".

# System Design: [Project Name]

## 1. Architecture Overview

High-level description of the system. What are the major components and how do they talk to each other?

Include a Mermaid diagram showing the main components and their relationships. Keep it high-level — boxes for services/components, arrows for data flow or communication. Don't model individual classes or functions.

Example diagram style (adapt to the actual project):

    ```mermaid
    graph TD
        Client[Web App] --> API[API Server]
        API --> DB[(Database)]
        API --> Cache[(Cache)]
        API --> Queue[Job Queue]
        Queue --> Workers[Background Workers]
        Workers --> DB
        Workers --> ExtAPI[External APIs]
    ```

After the diagram, briefly describe:

- The major components and what each one is responsible for
- How they communicate (REST, WebSocket, message queue, etc.)
- Any important architectural decisions or patterns (event-driven, CQRS, monolith vs. services, etc.)

## 2. Data Model

Define the core entities, their key attributes, and relationships. This is not a full database schema — it's a conceptual model that captures what data the system manages.

For each entity, list:

- Name
- Key attributes (the important ones, not every field — skip obvious things like id, created_at, updated_at)
- Relationships to other entities (and cardinality: one-to-many, many-to-many, etc.)

Include a Mermaid ER diagram showing the entities and their relationships.

Example:

    ```mermaid
    erDiagram
        USER ||--o{ PROJECT : owns
        PROJECT ||--o{ TASK : contains
        TASK }o--|| USER : "assigned to"
    ```

Call out any non-obvious modeling decisions: "We model X as a separate entity rather than a field on Y because..."

## 3. API Design

Define the key API endpoints or contracts. Focus on the main operations the system exposes — not every CRUD endpoint, but the ones that matter for understanding the system's behavior.

For each endpoint or operation, describe:

- What it does (in plain language)
- Key inputs and outputs (conceptual, not exact JSON schemas)
- Any important behavior notes (e.g., "this is async — returns immediately and processes in background")

Group endpoints by domain/resource. Use a simple table or list format:

| Operation      | Description                        | Key Input   | Key Output     | Notes                         |
| -------------- | ---------------------------------- | ----------- | -------------- | ----------------------------- |
| Create project | Set up a new project with defaults | name, owner | project object | Also creates default settings |

If the API has non-CRUD operations that are central to the product (e.g., "run analysis", "generate report", "match users"), give those extra attention — they're usually the interesting parts.

## 4. Frontend Structure

Describe the frontend at the level of pages/views and key interactive components. This is not a component tree — it's a map of what the user sees and interacts with.

Cover:

- **Pages / Views**: The main screens and what they show. A simple list or table is fine.
- **Key Components**: Interactive or complex components that are worth calling out (e.g., a real-time editor, a drag-and-drop board, a complex form wizard). Skip obvious ones (navbar, footer).
- **State Management Approach**: What state is global vs. local? What are the most complex state problems? (Don't prescribe a specific library — describe the state challenges.)
- **Data Flow**: How does data get to the frontend? What's cached? What's real-time? What requires optimistic updates?

## 5. Key Decisions & Tradeoffs

List the most important technical decisions embedded in this design, and for each one:

- What the decision is
- Why this approach was chosen
- What the main alternative would be
- What tradeoff is being made

These are the decisions that a team might debate or revisit. Making them explicit upfront saves time.

Example format:

**Monolith vs. microservices** — Start as a monolith with clear module boundaries. Splitting into services adds operational complexity that isn't justified at this scale. Revisit if specific components need independent scaling.
