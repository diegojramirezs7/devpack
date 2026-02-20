---
name: feature-implementation-plan
description: Transform a tech-agnostic feature specification (title, description, acceptance criteria) into a codebase-specific implementation plan. Use when the user has a defined feature and wants a concrete plan for implementing it in their repo. Designed for use with Claude Code. Common triggers include "plan this feature", "how would I implement this", "create an implementation plan", or when the user provides a feature spec and wants to know how to build it in their codebase.
---

# Implementation Planner

Transform a tech-agnostic feature specification into a codebase-specific implementation plan. This skill is designed to be used with Claude Code, where the repo is available as context.

## Input

This skill expects a feature specification as input, typically produced by the **feature-refiner** skill. The input should contain:

- **Title**: Name of the feature
- **Description**: 2-3 sentences on what the feature does and why
- **Acceptance Criteria**: A list of specific, testable criteria

If the input is missing any of these, ask the user to provide them before proceeding.

## Process Overview

1. **Receive the feature spec** — Parse the title, description, and acceptance criteria
2. **Explore the codebase** — Understand the repo's structure, tech stack, patterns, and conventions
3. **Identify the relevant code** — Find the files, components, and modules that the feature will touch
4. **Map criteria to code changes** — Determine what needs to change or be created for each acceptance criterion
5. **Detect risks and dependencies** — Surface anything that could block or complicate implementation
6. **Produce the plan** — Write a structured, actionable implementation plan

## Step 1: Receive the Feature Spec

Parse the provided feature spec. Echo it back in a summary to confirm understanding.

If the spec is ambiguous or seems incomplete, ask clarifying questions before exploring the codebase.

## Step 2: Explore the Codebase

Examine the repository to understand:

- **Project structure**: Directory layout, entry points, configuration files
- **Tech stack**: Languages, frameworks, libraries, build tools
- **Patterns and conventions**: How existing features are structured (routing, state management, data access, API patterns, component structure, naming conventions, test patterns)
- **Relevant existing code**: Files and modules that relate to the feature being planned

Focus your exploration on areas relevant to the feature. Don't map the entire repo — just what matters.

### What to look for

- How similar features are implemented (find the closest analog)
- Where new files should live based on existing conventions
- Which shared utilities, components, or services are available for reuse
- How tests are structured and what testing tools are used
- Any configuration or environment setup that may be needed

## Step 3: Identify Relevant Code

For each acceptance criterion, identify:

- **Files to modify**: Existing files that need changes, with specific locations (functions, classes, components)
- **Files to create**: New files needed, with where they should live based on project conventions
- **Shared code to reuse**: Existing utilities, components, hooks, services, or patterns that should be leveraged
- **Dependencies**: External packages that may need to be added

Be specific. Reference actual file paths, function names, component names, and patterns observed in the codebase.

## Step 4: Map Criteria to Code Changes

For each acceptance criterion, describe the concrete code changes:

- What functions/components/modules to create or modify
- How the change fits into existing patterns (e.g., "follow the same pattern as `src/features/auth/AuthService.ts`")
- Any data model or schema changes
- Any API endpoint changes
- Any UI component changes

## Step 5: Detect Risks and Dependencies

Surface anything that could complicate the implementation:

- **Blocking dependencies**: Does this require another feature or migration first?
- **Technical risks**: Are there areas of the codebase that are fragile, poorly tested, or poorly understood?
- **Pattern conflicts**: Does the feature require doing something the codebase doesn't currently support?
- **Performance concerns**: Could the implementation introduce performance issues?
- **Migration needs**: Does this require data migration, config changes, or environment updates?

## Step 6: Produce the Plan

### Output Format

```markdown
# [Feature Title]

## Description

[Echo back the feature description]

## Acceptance Criteria

[Echo back the acceptance criteria as provided]

## Plan

### Codebase Context

[Brief summary of the relevant tech stack, patterns, and conventions discovered during exploration. Mention the closest existing analog if one exists.]

### Implementation Steps

[Numbered list of concrete steps. Each step should include:]
[- What to do]
[- Which files to touch (specific paths)]
[- How it fits into existing patterns (with references to existing code)]
[- Any new files to create and where they go]

### Risks & Considerations

[Anything that could block or complicate the work. Include mitigations if obvious.]
```

### Plan Sizing

- If the plan can be executed in a single focused session, present it as a flat list of steps.
- If the plan is large (roughly more than 8-10 steps), divide it into **phases**. Each phase should be a coherent, independently testable chunk of work. Use the format:

```markdown
### Implementation Steps

#### Phase 1: [Phase Title]

[Goal of this phase in one sentence]

1. Step...
2. Step...

#### Phase 2: [Phase Title]

[Goal of this phase in one sentence]

1. Step...
2. Step...
```

### Guidelines for Good Steps

- **Be specific**: "Add a `calculateTotal` function to `src/services/cart.ts`" not "Add business logic"
- **Reference real code**: Use actual file paths, function names, and patterns from the repo
- **Follow existing conventions**: If the repo uses a particular pattern, the plan should follow it. Call out the pattern explicitly (e.g., "Follow the same service pattern as `OrderService.ts`")
- **Include test steps**: If the repo has tests, include steps for writing them, following the existing test conventions
- **Order logically**: Data model → business logic → API → UI is a common and sensible order, but follow whatever makes sense for the codebase
- **Note what to reuse**: Call out existing utilities, components, or helpers that should be leveraged rather than rebuilt

## Notes

- This skill assumes Claude Code has access to the repository and can read files
- The plan should be actionable enough that a developer (or Claude Code itself) could execute it step by step
- Prefer convention over invention — follow what the codebase already does
- If the codebase has no clear conventions in a relevant area, note that and suggest a reasonable approach
- The plan is a starting point, not a contract — expect adjustments during implementation
