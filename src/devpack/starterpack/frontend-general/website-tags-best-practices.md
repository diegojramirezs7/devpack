## Refined list

> Optimized for automated code review by an AI agent. Scan HTML source files and templates for each check. "Template files" includes any `.html`, `.php`, `.njk`, `.liquid`, `.astro`, `.vue`, `.jsx`/`.tsx` layout/page files that render a full document shell.

---

### 1. Doctype and `<html lang>`

**Scan for:**
- The file does not start with `<!doctype html>` (case-insensitive) as the very first line
- The `<html>` element is missing the `lang` attribute
- The `lang` attribute is present but empty (`lang=""`)
- The `lang` value doesn't match the primary written language of the page content (e.g. `lang="en"` on a Spanish-language page)

**Pass criteria:**
- `<!doctype html>` appears before any other content
- `<html lang="...">` uses a valid BCP 47 language tag (e.g. `en`, `en-US`, `fr`, `es-MX`)

**Flag as violation:**
- Missing `<!doctype html>`
- `<html>` tag with no `lang` attribute
- `lang=""` (empty value)
- `lang` value is a non-BCP-47 string (e.g. `lang="english"`, `lang="spanish"`)

---

### 2. Core Document Metadata — Charset and Viewport

**Scan for:**
- Missing `<meta charset="...">` in `<head>`
- `charset` value is not `utf-8` (e.g. `charset="iso-8859-1"`)
- Missing `<meta name="viewport" ...>` in `<head>`
- `viewport` content missing `width=device-width` or `initial-scale=1`
- `viewport` content includes `user-scalable=no` or `maximum-scale=1` (prevents zoom — accessibility failure)

**Pass criteria:**
- `<meta charset="utf-8" />` present in `<head>`, ideally as the first element
- `<meta name="viewport" content="width=device-width, initial-scale=1" />` present in `<head>`

**Flag as violation:**
- Missing charset meta tag
- `charset` value other than `utf-8`
- Missing viewport meta tag
- Viewport with `user-scalable=no` or `maximum-scale=1` (violates WCAG 1.4.4 — users cannot zoom)
- Viewport with `initial-scale` value other than `1`

---

### 3. SEO Fundamentals — Title, Description, Canonical, Robots

**Scan for:**

_Title:_
- Missing `<title>` element
- Empty `<title></title>`
- Generic/placeholder title text (e.g. "Page Title", "Untitled", "Home", "New Page", "Document")
- Multiple `<title>` elements in a single `<head>`

_Meta description:_
- Missing `<meta name="description">`
- Empty `content` attribute on the description tag
- Description `content` shorter than 50 characters (too vague) or longer than 160 characters (gets truncated in search results)

_Canonical:_
- Missing `<link rel="canonical" href="...">`
- `href` value is relative instead of absolute (must start with `https://`)
- `href` value is empty or a placeholder (e.g. `https://example.com`)

_Robots:_
- `<meta name="robots" content="noindex">` or `content="noindex,nofollow"` on pages that should be publicly indexed (flag for human review — may be intentional)

**Pass criteria:**
- `<title>` is present, unique per page, descriptive, and non-empty
- `<meta name="description">` has a `content` value between 50–160 characters
- `<link rel="canonical">` has an absolute `https://` URL unique to the page
- If `robots` is present, value is intentional and documented

**Flag as violation:**
- Missing or empty `<title>`
- Duplicate `<title>` tags
- Generic title text matching known placeholder strings
- Missing or empty meta description
- Description over 160 characters
- Canonical with a relative URL or placeholder domain
- `noindex` on what appears to be a public-facing page (flag for review)

---

### 4. Favicons

**Scan for:**
- Missing `<link rel="icon" type="image/svg+xml" href="...">` (SVG favicon)
- Missing `<link rel="icon" type="image/png" href="...">` (PNG fallback)
- Missing `<link rel="apple-touch-icon" href="...">`
- SVG favicon `href` pointing to a `.png` or `.ico` file
- PNG favicon `href` pointing to a non-PNG file
- `href` values that are empty or use placeholder paths (e.g. `/favicon.svg` with no file present — flag if you can verify)

**Pass criteria:**
- SVG favicon declared with `type="image/svg+xml"` and a `.svg` file path
- PNG favicon declared with `type="image/png"` and a `.png` file path (48×48px recommended)
- Apple touch icon declared with `rel="apple-touch-icon"` and a `.png` file path (180×180px recommended)
- All three `<link>` elements present in `<head>`

**Flag as violation:**
- Any of the three favicon `<link>` tags missing entirely
- `type` attribute mismatches the file extension in `href`
- Using only an `.ico` favicon with no SVG or PNG fallback

---

### 5. Open Graph (OG) Tags

**Scan for:**

_Required tags — flag if absent:_
- `<meta property="og:type" content="...">`
- `<meta property="og:url" content="...">`
- `<meta property="og:title" content="...">`
- `<meta property="og:description" content="...">`
- `<meta property="og:image" content="...">`
- `<meta property="og:image:alt" content="...">`
- `<meta property="og:site_name" content="...">`

_Value quality checks:_
- `og:url` `content` is a relative URL instead of absolute `https://`
- `og:url` `content` is a placeholder (e.g. `https://example.com`)
- `og:title` `content` is empty or matches a generic placeholder
- `og:description` `content` is empty
- `og:image` `content` is a relative path or placeholder URL
- `og:image:alt` `content` is empty (accessibility failure for social previews)
- `og:type` `content` is not a valid OG type for the page (typical values: `website`, `article`, `product`)

_Uniqueness:_
- `og:url` and `og:title` should be unique per page — flag if they use a hardcoded global value across all pages

**Pass criteria:**
- All 7 required OG tags present in `<head>`
- `og:url` is an absolute URL matching the page's canonical URL
- `og:title` and `og:url` are unique per page (not shared across all pages)
- `og:image` is an absolute URL; image should be at least 1200×630px (cannot be verified statically, note as advisory)
- `og:image:alt` is non-empty and describes the image

**Flag as violation:**
- Any of the 7 required tags missing
- Empty `content` attributes
- Relative URLs in `og:url` or `og:image`
- `og:image:alt` missing or empty
- Placeholder domain (`example.com`) in any URL field

---

### 6. Twitter / X Meta Tags

**Scan for:**
- Missing `<meta name="twitter:card" content="...">` — this is the only required Twitter tag
- `twitter:card` `content` value is not one of the valid types: `summary`, `summary_large_image`, `app`, `player`
- If `twitter:title`, `twitter:description`, `twitter:image`, or `twitter:image:alt` are present, check they are non-empty (they are optional but if declared must have values)

**Pass criteria:**
- `<meta name="twitter:card">` is present with a valid card type (typically `summary_large_image` for most pages)
- Any optional Twitter tags that are declared have non-empty `content` values
- Note: if Twitter-specific tags are absent, OG tags serve as fallback — this is acceptable

**Flag as violation:**
- `twitter:card` present but `content` is empty or an invalid card type
- Any declared `twitter:*` tag with an empty `content` attribute
- `twitter:image` declared without a corresponding `twitter:image:alt` (accessibility issue — same as OG)

---

### 7. Skip Navigation Link

**Scan for:**
- No `<a>` element with an `href` pointing to an in-page anchor (e.g. `href="#main"`, `href="#content"`) as the first or near-first child of `<body>`
- Skip link present but its `href` target ID does not exist in the document (e.g. `href="#main"` but no `id="main"` or `<main>` anywhere on the page)
- Skip link present but not visually hidden when unfocused — it should be off-screen or hidden via CSS until focused
- Skip link present but lacks a focus style, making it invisible when keyboard users tab to it
- Skip link is placed after other focusable elements (it must be the first focusable element on the page)

**Pass criteria:**
- A skip link `<a href="#[target]">Skip to main content</a>` (or equivalent wording) is the first focusable element inside `<body>`
- The anchor target (e.g. `id="main"`) exists on the page, typically on the `<main>` element
- The skip link is visually hidden until focused (via `visually-hidden-focusable`, `sr-only`, or equivalent CSS class)
- The skip link has a visible focus style when focused

**Flag as violation:**
- No skip link present at or near the start of `<body>`
- Skip link `href` target ID is not present in the document
- Skip link is not the first focusable element (other links, buttons, or inputs appear before it)
- Skip link is permanently hidden with `display: none` or `visibility: hidden` (unfocusable — defeats the purpose)