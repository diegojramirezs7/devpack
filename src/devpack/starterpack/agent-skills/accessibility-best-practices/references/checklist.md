# Accessibility Checklist

7 high-impact WCAG 2.1 checks. For each one: what to scan for, what passes,
and what to flag as a violation.

---

## 1. Non-text Content — Alt Text (SC 1.1.1, Level A)

### Scan for
- `<img>` elements missing the `alt` attribute entirely
- `<img alt="">` on images that appear informational (not decorative)
- `alt` text that is a filename, URL, or generic string (e.g. `alt="image.jpg"`, `alt="photo"`, `alt="icon"`)
- `<svg>` elements lacking `role="img"` and `aria-label` / `aria-labelledby` / `<title>`
- Icon buttons (e.g. `<button><svg>...</svg></button>`) with no accessible name
- Image `<input type="image">` missing `alt`
- Complex images (charts, diagrams) with only a short `alt` and no `aria-describedby` or linked long description

### Pass criteria
- Informational images: `alt` text describes the purpose or content, not the visual appearance
- Decorative images: `alt=""` (empty string) and no `role`
- Icon-only interactive controls: accessible name via `aria-label`, `aria-labelledby`, or visually-hidden text
- Complex images: short `alt` identifying content type + long description linked or adjacent

### Flag as violation
- Missing `alt` on any `<img>`
- `alt` value equals the filename or contains only generic words
- SVG used as meaningful content without an accessible name
- Icon buttons with no text alternative

---

## 2. Headings and Labels — Descriptive (SC 2.4.6, Level AA)

### Scan for
- Heading elements (`<h1>`–`<h6>`) whose text content is vague or generic (e.g. "Section", "More", "Info", "Untitled", numbered sequences like "Section 1")
- `<label>` elements or `aria-label` / `placeholder` values that are generic (e.g. "Field", "Input", "Enter here")
- Form inputs (`<input>`, `<select>`, `<textarea>`) with no associated `<label>`, `aria-label`, or `aria-labelledby`
- Inputs relying solely on `placeholder` as the label (placeholder disappears on input)
- Icon-only labels without accompanying text or a commonly understood `aria-label`

### Pass criteria
- Each heading clearly identifies the topic of the section that follows
- Every form control has a label that describes the expected input
- Labels are accurate — they match the actual purpose of the field or section

### Flag as violation
- Heading text that gives no indication of section content
- Form inputs with missing or non-descriptive labels
- `placeholder` used as the only label substitute

---

## 3. Contrast Minimum (SC 1.4.3, Level AA)

### Scan for
- Inline `style` attributes and CSS with hardcoded foreground color (`color:`) without a corresponding background color, or vice versa
- Color values in CSS/Tailwind/styled-components that produce known low-contrast pairings (e.g. light gray text on white)
- Text rendered inside images (check design assets or `<canvas>` elements)
- Placeholder text styles (often rendered at reduced opacity — verify computed contrast)
- Hover and focus state text/background color overrides

### Pass criteria (exact thresholds — do not round)
- Normal text (< 18pt regular / < 14pt bold): contrast ratio ≥ **4.5:1**
- Large text (≥ 18pt regular / ≥ 14pt bold): contrast ratio ≥ **3:1**
- Disabled/inactive UI components and pure decorative text are exempt
- Logotypes and brand names are exempt

### Flag as violation
- `color` specified without `background-color` (or vice versa) on text elements — browser default cannot be assumed
- Any computed contrast ratio below thresholds (use a contrast checker with exact hex values)
- Placeholder text with opacity less than ~0.5 on a white background (typically fails 4.5:1)

---

## 4. Focus Visible (SC 2.4.7, Level AA)

### Scan for
- CSS rules that remove focus outlines globally: `outline: none`, `outline: 0`, `*:focus { outline: none }`, `:focus { box-shadow: none }` without a replacement style
- Interactive elements (`<a>`, `<button>`, `<input>`, `<select>`, `<textarea>`, elements with `tabindex`) that have no `:focus` or `:focus-visible` style defined
- JavaScript event handlers calling `.blur()` immediately after `.focus()`, or `event.preventDefault()` on `keydown` for Tab key
- Custom components (dropdowns, modals, date pickers) that intercept keyboard events but don't restore or manage focus

### Pass criteria
- Every keyboard-focusable element shows a visible indicator when focused (native browser default is acceptable if not overridden)
- Custom components that receive focus display a visible custom indicator (border, outline, background change)
- Focus is never programmatically removed (`blur()`) in response to the user tabbing to an element

### Flag as violation
- Global `outline: none` / `outline: 0` without a `:focus-visible` replacement
- Any interactive element with no `:focus` or `:focus-visible` styling at all
- Scripts that call `.blur()` when an element receives focus (WCAG F55)
- CSS that sets focus indicator to invisible, e.g. same color as background (WCAG F78)

---

## 5. Link Purpose (SC 2.4.4, Level A)

### Scan for
- `<a>` elements whose visible text (or `aria-label`) is ambiguous out of context: "click here", "here", "read more", "learn more", "more", "details", "link", "this", "download"
- Multiple links on the same page with identical link text but different `href` values
- Image-only links (`<a><img></a>`) where the `<img>` has `alt=""` or no `alt` — the link has no accessible name
- Icon-only links without `aria-label` or visually-hidden text
- Links whose `aria-label` contradicts the visible text (misleading)

### Pass criteria
- Link purpose is clear from link text alone, OR from link text + immediately surrounding sentence/list item/table cell
- When multiple links go to different destinations, each has unique descriptive text or a unique `aria-label`
- Image-only links have a descriptive `alt` on the image or `aria-label` on the `<a>`

### Flag as violation
- Any `<a>` with text matching the ambiguous list above, with no supplementary `aria-label` or `aria-describedby`
- `<a>` containing only an `<img>` where `alt=""` or `alt` is missing (WCAG F89)
- Duplicate link text pointing to different URLs without differentiation

---

## 6. Meaningful Sequence — DOM Order (SC 1.3.2, Level A)

### Scan for
- CSS `position: absolute/fixed` or CSS Grid/Flexbox `order` property used to visually reorder content in a way that differs from DOM order
- `tabindex` values greater than 0 (e.g. `tabindex="2"`) which override natural tab order
- Layout tables (`<table>` used for visual layout, not data) that won't linearize logically
- Content split across columns or positioned elements where reading order in DOM doesn't match visual left-to-right, top-to-bottom flow
- Navigation menus, sidebars, or modals that appear visually early but are placed late in the DOM (or vice versa)

### Pass criteria
- DOM source order matches the intended reading/interaction order when CSS is disabled
- `tabindex` is only `0` or `-1` — never a positive integer
- Data tables use `<th>`, `scope`, and `headers` to convey relationships when linearized

### Flag as violation
- CSS reordering (flex `order`, `position`) that changes meaning when styles are removed (WCAG F1)
- Layout tables that produce nonsensical reading order when linearized (WCAG F49)
- Any `tabindex` value > 0
- Whitespace or `<br>` used for visual spacing instead of semantic structure (WCAG F32/F33)

---

## 7. Keyboard Accessibility (SC 2.1.1, Level A)

### Scan for
- Event handlers attached only to mouse events without keyboard equivalents:
  - `onclick` on non-interactive elements (`<div>`, `<span>`) with no `tabindex` and no `onkeydown`/`onkeypress`
  - `onmouseover`/`onmouseout` for showing/hiding content with no `onfocus`/`onblur` equivalent
  - `ondblclick` with no keyboard alternative
- Custom interactive components (accordions, tabs, carousels, dropdowns, date pickers, drag-and-drop) missing keyboard event handlers
- Elements that should be interactive (visually styled as buttons/links) but are `<div>` or `<span>` without `tabindex="0"` and keyboard handlers
- Emulated links (`<span>` with `onclick`) that don't respond to Enter key (WCAG F42)
- Mouse-only event handlers on custom widgets (WCAG F54)

### Pass criteria
- All interactive functionality is operable via keyboard alone (Tab, Shift+Tab, Enter, Space, arrow keys as appropriate)
- Custom widgets follow ARIA authoring practices for keyboard interaction (e.g. arrow keys for tabs/menus, Escape to close modals)
- No functionality requires a specific timing of keystrokes

### Flag as violation
- `<div role="button">` or `<span>` with click handler but no `tabindex` or keyboard event handler
- `onmouseover` revealing content with no `onfocus` equivalent
- Custom components that capture Tab key without providing a way to exit (keyboard trap — also violates SC 2.1.2)
- Mouse-drag interactions with no keyboard alternative