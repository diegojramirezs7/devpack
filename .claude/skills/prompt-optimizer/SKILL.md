---
name: prompt-optimizer
description: Optimize and refine LLM prompt templates according to proven best practices. Use this skill whenever the user wants to improve a prompt, write a better prompt, review a prompt for issues, create a high-quality prompt from a goal description, or refactor an existing prompt template. Also trigger when the user mentions "prompt engineering", "prompt optimization", "improve my prompt", "write a system prompt", "make this prompt better", or shares a prompt and asks for feedback. Works for all prompt types including system prompts, data extraction, classification, content generation, and evaluation prompts.
---

# Prompt Optimizer

A skill for transforming rough prompt drafts or goal descriptions into well-structured, high-performing LLM prompts.

## When to use

- The user provides a draft prompt and wants it improved
- The user describes what they want a prompt to accomplish and needs one written from scratch
- The user asks for a prompt review or critique

## First step — always

Read the best practices reference before doing anything:

```
view /path/to/skill/references/best-practices.md
```

This document contains the prompt engineering principles that guide every optimization decision. Read it fresh each time — don't rely on memory.

## Understanding the input

The user will give you one of two things:

1. **A draft prompt** they've already written — could be rough, could be nearly done, could be a system prompt, a one-shot template, or anything in between.
2. **A goal description** — what they want the prompt to accomplish, the context it'll be used in, and what kind of output they expect.

If the input is ambiguous or missing critical details, ask clarifying questions before proceeding. The key things you need to know:

- **What task** the prompt needs to accomplish
- **Who/what** will be executing it (which model, what context — API call, chatbot, agent, pipeline step)
- **What the input looks like** — what data or content will be fed into the prompt at runtime
- **What the output should look like** — format, structure, length, style, and any downstream consumers
- **What's going wrong** (if they have a draft) — where is the current prompt falling short?

Don't over-interrogate. If you have enough to work with, proceed. You can always refine in a follow-up iteration.

## The optimization process

### Analyzing the prompt (or goal)

Before writing anything, think through these dimensions. You don't need to list them all out to the user — this is your internal checklist:

**Structure & clarity**

- Is there a clear task description with role/persona?
- Is context separated from instructions?
- Are delimiters used to distinguish input data from instructions?
- Is the most important information placed at the beginning or end (strategic positioning)?

**Specificity**

- Are requirements stated positively (what TO do, not what NOT to do)?
- Are constraints, edge cases, and uncertainty handling addressed?
- Is the output format explicitly defined?
- Are scoring systems, rubrics, or evaluation criteria specified where relevant?

**Reasoning support**

- Does the task require complex reasoning? If so, does the prompt encourage step-by-step thinking?
- Are intermediate steps or scratchpad areas built in?
- Is the model given room to "think" before producing a final answer?
- Are specific reasoning steps outlined, or is it left as a generic "think step by step"?

**Grounding & examples**

- Would few-shot examples help reduce ambiguity?
- Is reference material provided where accuracy matters?
- Are examples well-chosen and minimal (not excessive)?

**Task decomposition**

- Is this prompt trying to do too much at once?
- Would it benefit from being broken into chained sub-prompts?
- Should classification happen before processing?

**Output control**

- Is the output format fully specified (structure, length, style)?
- Will the output feed into a downstream system that needs a specific format?
- Are edge-case outputs handled (empty input, ambiguous cases, errors)?

### Writing the optimized prompt

Build the prompt using this structural framework, adapting it to the specific use case. Not every prompt needs every section — use judgment about what's relevant.

#### Structural template

```
[ROLE / PERSONA]
Who the model is and what expertise it brings. Only include if it
meaningfully shapes the response quality or perspective.

[CONTEXT / BACKGROUND]
Background information the model needs to do the task well.
Grounding data, domain knowledge, or reference material.

[TASK DESCRIPTION]
Clear, specific description of what the model must do.
State requirements positively. Address edge cases.
Include step-by-step reasoning instructions if the task is complex.

[INPUT SPECIFICATION]
What the model will receive at runtime. Use delimiters to mark
where dynamic content goes.

  <<<
  {{input_placeholder}}
  >>>

[OUTPUT SPECIFICATION]
Exact format, structure, and constraints for the response.
Include an example of the desired output if the format is non-obvious.

[EXAMPLES] (if needed)
1-3 well-chosen input/output pairs that demonstrate the expected behavior.
Focus on cases that clarify ambiguity — don't add examples for obvious behavior.
```

#### Writing principles

These come directly from the best-practices reference and should guide every decision:

- **Positive framing**: Say what to do, not what to avoid. "Respond in formal English" beats "Don't use slang."
- **Delimiter discipline**: Always separate instructions from dynamic content using clear markers (`<<<>>>`, `"""`, `###`, XML tags, etc.). This prevents the model from confusing data with instructions.
- **Strategic positioning**: Place the most critical instructions at the very beginning and very end of the prompt. Models attend most strongly to these positions.
- **Calibrated examples**: Use few-shot examples only when instructions alone can't convey the desired behavior. For complex formatting or domain-specific tasks, 2-3 examples are valuable. For straightforward tasks, zero-shot is fine.
- **Reasoning scaffolding**: For any task requiring judgment, analysis, or multi-step logic, explicitly instruct the model to reason before answering. Be specific about what reasoning steps to follow rather than just saying "think step by step."
- **Output precision**: Define output format down to the level of detail that matters. If it feeds into code, specify JSON schema. If it's for humans, specify tone, length, and structure.
- **Minimal completeness**: Include everything the model needs, but nothing it doesn't. Extra instructions that don't help the task actively hurt — they dilute attention from what matters.

### Handling different prompt types

**System prompts for agents/assistants**

- Lead with persona and behavioral boundaries
- Define the scope of what the agent should and shouldn't do
- Include guidance for handling ambiguous or out-of-scope requests
- Structure with clear sections (role, capabilities, constraints, response format)

**Data extraction / analysis prompts**

- Specify input format and expected output schema precisely
- Include handling for missing, malformed, or ambiguous data
- Use chain-of-thought for multi-step extraction logic
- Provide 1-2 examples showing input → output mapping

**Classification / evaluation prompts**

- Define categories or scoring criteria exhaustively
- Include rubrics with clear boundaries between categories
- Instruct the model to reason about its classification before committing
- Handle edge cases and "uncertain" classifications explicitly

**Content generation prompts**

- Specify tone, audience, length, and structure
- Provide reference examples of the desired style if non-obvious
- Include constraints on what to include/exclude
- Define quality criteria the output should meet

## Delivering the output

Save the optimized prompt as a clean markdown file. The file should contain only the prompt — no meta-commentary, no changelog, no rationale section. Just the prompt, ready to copy and use.

Use a descriptive filename like `optimized-prompt-[short-description].md`.

Before saving, do a final pass checking:

- Every section serves a purpose
- No redundant or contradictory instructions
- Delimiters are consistent throughout
- Output format is unambiguous
- The prompt reads naturally when you imagine the model encountering it cold

After presenting the file, briefly mention (in chat, not in the file) 2-3 of the most impactful changes you made and why — this helps the user learn and iterate.

## Iteration

Prompt optimization is iterative. After delivering the first version, be ready for the user to:

- Test it and come back with issues
- Ask for adjustments to specific sections
- Want a variation for a different use case
- Share sample outputs that aren't quite right

Each iteration should re-read the best practices reference and apply the same rigor as the initial optimization.
