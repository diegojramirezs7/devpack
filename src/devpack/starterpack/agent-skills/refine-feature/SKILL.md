---
name: refine-feature
description: Transform rough, unstructured feature ideas into well-defined, implementation-ready features with clear scope and acceptance criteria. Use when the user asks to refine, clarify, break down, or scope feature ideas for their applications or projects. Common triggers include "help me refine this feature", "break down this idea", "scope this feature", or when the user provides unstructured notes about what they want to build.
metadata:
  tags:
    - general
---

# Feature Refiner

Transform rough feature ideas into clear, actionable feature definitions optimized for continuous delivery.

## Process Overview

Follow this collaborative refinement process:

1. **Understand the raw input** - Parse unstructured notes and identify all distinct ideas
2. **Identify the core feature** - Determine the primary user problem or capability
3. **Organize related points** - Group notes that belong to the same feature
4. **Surface separated concerns** - Flag notes that should become separate features
5. **Apply continuous delivery principles** - Ensure the feature is appropriately sized
6. **Define minimum ideal version** - Identify the smallest valuable implementation
7. **Produce clean specification** - Create structured markdown output

## Step 1: Understand the Input

Parse the user's unstructured notes to:

- List all distinct ideas or points mentioned
- Identify any explicit requirements or constraints
- Note any technical details or dependencies mentioned
- Flag any ambiguous or unclear points

## Step 2: Identify the Core Feature

Determine what the main feature is by asking:

- What user problem is being solved?
- What is the primary capability being added?
- If multiple capabilities are mentioned, which is the central one?

**Confirm with the user**: "Based on your notes, it seems the core feature is [X]. Is that correct?"

## Step 3: Organize Related Points

Group the notes into:

- **Core feature points**: Directly related to the main capability
- **Separate features**: Should become their own feature (too complex or tangentially related)
- **Future considerations**: Nice-to-haves or enhancements for later iterations

For items that should be separate features, briefly explain why they deserve separation.

## Step 4: Apply Continuous Delivery Principles

Consult [cd_principles.md](references/cd_principles.md) to evaluate if the feature needs to be broken down further.

Ask the user:

- "This feature might be too large for one iteration. Should we break it into: [option A], [option B]?"
- "Would you prefer to start with [simpler version] and add [complex parts] later?"

## Step 5: Surface Issues and Considerations

Help the user think through:

- **Edge cases**: "What should happen if [edge case]?"
- **Dependencies**: "This feature seems to depend on [X]. Does that already exist?"
- **Technical challenges**: "Have you considered how [technical aspect] will work?"
- **User experience**: "How should users discover/access this feature?"
- **Related ideas**: "This makes me think of [related concept]. Is that in scope?"

Present these as collaborative questions, not prescriptive statements.

## Step 6: Define Minimum Ideal Version

Identify what can be omitted from the first iteration while still delivering value:

- What's the happy path that must work?
- What validations can be added later?
- What edge cases can be deferred?
- What UI polish can come in a follow-up?

**Confirm with user**: "For the minimum version, I think we should include [X] but defer [Y]. Does that align with your goals?"

## Step 7: Produce Final Output

Create a clean markdown document with:

```markdown
# [Feature Title]

[2-3 sentence description of what the feature does and why it matters]

## Acceptance Criteria

- [ ] [Specific, testable criterion]
- [ ] [Another criterion]
- [ ] [etc.]

## Out of Scope (Future Considerations)

- [Item deferred to later]
- [Another deferred item]

## Separated Features

- **[Feature Name]**: [Brief description] - [Why it should be separate]
```

### Acceptance Criteria Guidelines

Write criteria that are:

- **Specific**: Clear, unambiguous actions or states
- **Testable**: Can be verified as complete or incomplete
- **User-focused**: Describe outcomes, not implementation details
- **Independent**: Each criterion stands alone
- **Concise**: 5-8 criteria is typical; more suggests the feature is too large

## Collaborative Approach

Throughout the process:

- **Ask questions** rather than making assumptions
- **Propose options** rather than dictating solutions
- **Seek confirmation** at key decision points
- **Explain reasoning** when suggesting separations or simplifications
- **Stay flexible** - the user knows their domain best

## Example Interaction Flow

```
User: Help me refine this feature: [pastes unstructured notes]

Claude:
1. [Summarizes understanding of notes]
2. "It seems the core feature is [X]. Is that right?"
3. [Wait for confirmation]
4. [Groups related points, flags separate features]
5. "I think [these points] should be a separate feature because [reason]. Do you agree?"
6. [Discusses minimum version options]
7. [Asks about edge cases and dependencies]
8. [Produces final markdown document]
```

## Notes

- User notes are typically unstructured text, bullet points, or markdown
- Multiple rounds of refinement are normal and expected
- Focus on continuous delivery: small, valuable, testable increments
- The goal is clarity and actionability, not perfection
