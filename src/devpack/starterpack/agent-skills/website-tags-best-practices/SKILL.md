---
name: website-tags-best-practices
description: Check and enforce proper HTML document structure, meta tags, SEO fundamentals, favicons, Open Graph tags, Twitter cards, and skip navigation in web apps. Use this skill whenever you are creating a new HTML page, layout template, or document shell — including .html, .php, .njk, .liquid, .astro, .vue, .jsx/.tsx files that render a full page. Also trigger when the user mentions SEO, meta tags, OG tags, social sharing previews, favicons, document head, or page templates. Even if the user doesn't explicitly ask, apply these checks whenever you're writing or reviewing a file that contains a <head> or <html> element.
metadata:
  tags:
    - frontend
---

# HTML Standards Skill

Enforce proper document structure and metadata when writing or reviewing web
page templates. This skill covers 7 checks spanning doctype, charset, viewport,
SEO tags, favicons, social meta tags, and skip navigation.

## How to use this skill

**When creating new pages or layouts:** Apply the checklist proactively. Every
new document shell should include all required elements from the start — don't
ship a `<head>` with just a `<title>` and plan to "add the rest later."

**When reviewing existing templates:** Scan the file against each of the 7
checks in `references/checklist.md`. Report what you find and fix it.

**Output format:** Fix the code directly, then provide a brief summary of what
was changed and why — grouped by check. If no issues are found for a category,
skip it.

## Workflow

1. Read `references/checklist.md` to load the full set of checks
2. Determine if the file is a full document template (contains `<html>` or
   `<head>` or renders a document shell). If it's a partial/component, most
   checks won't apply — skip gracefully.
3. Scan against each applicable category
4. Fix violations inline
5. After all fixes, summarize changes like this:

```
### HTML standards fixes applied

**Doctype & lang (Check 1):** Added missing `lang="en"` to `<html>` tag.

**SEO (Check 3):** Added `<meta name="description">` and
`<link rel="canonical">`. Title was a placeholder ("Document") — flagged
for the developer to write a real one.

**Open Graph (Check 5):** Added all 7 required OG tags. `og:image:alt`
was missing.
```

Only list categories where you made changes or found issues worth flagging.

## Severity guidance

- **Must fix:** Missing doctype, missing `lang`, missing charset, missing
  viewport, `user-scalable=no` (blocks zoom), missing `<title>`, no skip
  link — these cause real problems for users, search engines, or assistive
  technology.
- **Should fix:** Missing meta description, missing canonical, missing
  favicons, missing OG tags, missing Twitter card — these degrade SEO and
  social sharing.
- **Flag for review:** `noindex` on a public page, generic placeholder
  title text, hardcoded OG values shared across pages — these might be
  intentional but are worth a second look.

## Scope

This skill applies to **full document templates** — files that render a
complete HTML page with `<!doctype html>`, `<html>`, `<head>`, and `<body>`.

It does **not** apply to partial components, fragments, or files that only
render inner page content. If a file has no `<html>` or `<head>` element,
skip this skill.

## What this skill does NOT cover

- Content quality (whether the title/description are _good_, just whether
  they exist and aren't obviously placeholder text)
- Verifying that favicon files actually exist on disk (flag suspicious paths)
- Checking actual OG image dimensions (note the 1200×630 recommendation
  as advisory)
- Runtime behavior or server-rendered meta tags injected by JavaScript
