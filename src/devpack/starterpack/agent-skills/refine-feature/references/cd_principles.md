# Continuous Delivery Principles for Feature Sizing

## Core Principles

**Small batch sizes**: Features should be small enough to:
- Be completed in 1-3 days of development work
- Be tested thoroughly without excessive test suites
- Be rolled back easily if issues arise
- Provide value independently or as part of a clear sequence

**Vertical slicing**: Each feature should cut through all layers (UI, business logic, data) rather than implementing one layer across multiple features.

**Iterative refinement**: Start with the simplest version that delivers value, then enhance in subsequent iterations.

## Breaking Down Features

### Signs a feature is too large:
- Takes more than a week to implement
- Touches too many systems or components
- Has many conditional branches or edge cases
- Description includes "and" multiple times
- Acceptance criteria list exceeds 8-10 items

### Strategies for breaking down:
1. **By user journey steps**: Each step becomes its own feature
2. **By workflow variations**: Start with happy path, add error handling later
3. **By data operations**: Create → Read → Update → Delete as separate features
4. **By user roles**: Implement for one role first, expand later
5. **By constraints**: Start without constraints, add validation incrementally

## Minimum Ideal Version

The minimum ideal version should:
- Solve the core user problem
- Be usable end-to-end (even if limited)
- Omit nice-to-haves and edge case handling
- Enable learning and feedback
- Not compromise architectural integrity

Ask: "What's the smallest thing we could ship that would still be valuable?"