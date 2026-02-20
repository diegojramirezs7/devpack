---
name: accessibility-best-practices
description: Review and enforce WCAG accessibility best practices when writing or reviewing frontend code. Use this skill whenever you are writing new UI components, reviewing existing HTML/JSX/CSS, refactoring frontend code, or when the user mentions accessibility, a11y, WCAG, screen readers, keyboard navigation, or asks for an accessibility audit. Also trigger when working on forms, images, links, navigation, modals, or any interactive widgets — these are high-risk areas for accessibility issues. Even if the user doesn't explicitly mention accessibility, apply these checks whenever you're touching frontend code.
---

# Accessibility Review Skill

Apply WCAG 2.1 Level A and AA best practices when writing or reviewing frontend
code. This skill covers 7 high-impact success criteria. The goal is to catch
real violations and fix them — not to rubber-stamp code or produce vague
warnings.

## How to use this skill

**When writing new code:** Apply the checklist proactively as you write. Don't
generate code that violates these rules in the first place. If you catch
yourself about to write a `<div onClick>` without keyboard handling, fix it
before it hits the file.

**When reviewing existing code:** Scan the code against each of the 7 checks
in `references/checklist.md`. Report what you find and fix it.

**Output format:** Fix the code directly, then provide a brief summary of
what was changed and why — grouped by success criterion. If no issues are
found for a category, skip it; don't pad the summary with "no issues found"
for every single rule.

## Workflow

1. Read `references/checklist.md` to load the full set of checks
2. Scan the code file(s) against each applicable category
3. Fix violations inline
4. After all fixes, summarize changes like this:

```
### Accessibility fixes applied

**Alt Text (SC 1.1.1):** Added descriptive `alt` to 3 product images that
had `alt="image.jpg"`. Marked the decorative divider image with `alt=""`.

**Keyboard (SC 2.1.1):** Converted `<div onClick>` dropdown trigger to
`<button>` with `onKeyDown` handler for Enter/Space.
```

Only list categories where you made changes or found issues worth flagging.

## Severity guidance

Not all violations are equal. Use your judgment:

- **Must fix:** Missing alt text, keyboard traps, no focus indicator at all,
  form inputs with no label — these block real users.
- **Should fix:** Generic link text ("click here"), vague headings, positive
  tabindex values — these degrade the experience.
- **Worth noting:** Contrast concerns you can't fully verify without computed
  styles, reading order that _might_ differ from visual order — flag these
  for the developer to check manually.

## Framework-agnostic

These rules apply regardless of framework. Adapt the specific syntax:

- **Plain HTML:** Check elements directly
- **React/JSX:** Check JSX output — `className` instead of `class`,
  `htmlFor` instead of `for`, `onClick` handlers on non-interactive elements
- **Vue/Svelte/etc.:** Same principles, different template syntax
- **Tailwind/CSS-in-JS:** Check for `outline-none` / `outline-0` classes
  without a focus-visible replacement

## What this skill does NOT cover

This is a code-level static review. It cannot:

- Compute actual contrast ratios from rendered styles (flag suspicious
  pairings and recommend manual verification)
- Test real keyboard/screen reader behavior at runtime
- Evaluate content quality (whether alt text is _good_, just whether it exists
  and isn't obviously wrong)
- Cover every WCAG criterion — this focuses on the 7 highest-impact checks

When in doubt, flag it and let the developer decide.
