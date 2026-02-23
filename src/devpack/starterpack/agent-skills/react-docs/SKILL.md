---
name: react-docs
description: >
  Generates documentation for React applications. Use this skill whenever the user wants
  to document a React app — whether that means adding JSDoc comments to a specific component
  or file, or generating a high-level spec document for an entire React project. Trigger
  this skill for any request like "document this component", "add JSDoc to my hooks",
  "generate a spec for my React app", "document my Redux store", or anytime a .tsx/.ts/.jsx
  file from a React project is being discussed and documentation is the goal.
metadata:
  tags:
    - react
    - nextjs
---

# React Documentation Skill

This skill has two modes:

- **Component mode**: Reads a React source file and adds JSDoc comments inline. No companion markdown — just clean, well-documented source code.
- **App spec mode**: Scans an entire React project and produces a single structured `SPEC.md` giving a high-level architectural overview.

You can run either mode independently or both together.

---

## Component Mode

### When to use it

The user points you at a specific file or set of files: a component (`.tsx`, `.jsx`), a custom hook, a Redux/Zustand store slice, a React Query query/mutation file, a utility, or a type definition file.

### What to do

**Step 1 — Read the file carefully.**
Understand what the component or module does before writing anything. Pay attention to props, internal state, side effects, what data it fetches, and how it connects to global state.

**Step 2 — Add JSDoc comments directly to the source file.**
Edit the actual file. Rules:

**For components:**
- Add a JSDoc block above the component function describing its purpose, where it's used, and anything non-obvious about its behavior.
- Document the props interface or type with `@param` for each prop — name, type, and a short description. If TypeScript types are already explicit and self-explanatory, you can skip restating the type and focus on the *meaning*.
- If the component has significant internal state, briefly note the key pieces with inline comments rather than a full JSDoc block — keep it light.
- Document `useEffect` blocks with a short inline comment explaining *why* the effect exists, not just what it does. Side effects are where bugs hide; a good comment here saves hours.

**For custom hooks:**
- JSDoc block describing what the hook does, what it returns, and any important caveats (e.g. "must be used inside a Redux Provider").
- `@param` for each argument.
- `@returns` describing the shape of the return value, especially if it's an object with multiple fields.

**For Redux slices / Zustand stores:**
- JSDoc on the store/slice itself explaining what domain state it owns.
- Comment on each action/reducer explaining what triggers it and what it changes.
- Document selectors with what they derive and any memoization in play.

**For React Query files:**
- Document each query/mutation hook: what endpoint it hits, what it returns, and any key options (e.g. stale time, enabled conditions).

**General rules:**
- Don't over-document. If the code is clear, a one-liner is enough. Focus on *why* and *what*, not *how* when the code already shows that.
- Don't restate TypeScript types in prose when they're already explicit — add meaning, not noise.
- If something is genuinely confusing or non-standard, say so in the comment. Be honest.

**Example — component:**
```tsx
/**
 * Displays a paginated list of user orders with filtering by status.
 * Used on the Account page. Fetches data via React Query and reads
 * filter state from the orders Redux slice.
 */
const OrderList: React.FC<OrderListProps> = ({ userId, pageSize = 20 }) => {
```

**Example — hook:**
```tsx
/**
 * Fetches and caches the current user's profile data.
 * Automatically refetches when the auth token changes.
 *
 * @returns The user profile, loading state, and a refetch function.
 */
export function useUserProfile() {
```

**Example — useEffect:**
```tsx
// Sync selected filters to URL params so the page is shareable
useEffect(() => {
```

---

## App Spec Mode

### When to use it

The user asks for a project-level overview, a spec, or an architectural summary of their React app.

### What to do

**Step 1 — Explore the project structure.**
Walk the directory tree. Identify the router setup, the pages/routes, the global state solution (Redux, Zustand, Context, etc.), and any data-fetching layer (React Query, SWR, plain fetch, etc.). Look for `package.json` to understand key dependencies.

**Step 2 — Read the key files.**
Prioritize:
- Router configuration (where routes are defined)
- Page-level components (components that map to routes)
- Store setup: Redux root reducer / Zustand stores / Context providers
- Any shared API client or query configuration (e.g. React Query's `QueryClient` setup, Axios instance)
- `package.json` for major dependencies and scripts
- Environment config (`.env.example` or similar)

You don't need to read every component — focus on the skeleton, not the leaves.

**Step 3 — Write `SPEC.md` in the project root.**

Use this fixed template:

```markdown
# <Project Name> — App Spec

> One-paragraph summary of what this application does and who it's for.

---

## Page & Route Structure

Map each route to its page component and a short description of what it does.

| Path | Component | Description | Auth Required |
|------|-----------|-------------|---------------|
| `/` | `HomePage` | Landing page, shows summary dashboard | No |
| `/login` | `LoginPage` | Email/password login form | No |
| `/orders/:id` | `OrderDetailPage` | Detail view for a single order | Yes |
[...]

Note any nested routing, layout wrappers, or dynamic route patterns worth explaining.

---

## State Management Architecture

- **Solution in use**: (e.g. Redux Toolkit, Zustand, React Context, or a combination)
- **Store structure**: List the main slices/stores and what domain each owns.
  - `authSlice` — current user, token, login/logout state
  - `ordersSlice` — order list, filters, pagination
  - [...]
- **Key patterns**: Note anything non-standard — middleware, custom selectors, derived state, persistence (e.g. redux-persist).

---

## API Calls & Data Flow

- **Data fetching approach**: (e.g. React Query with Axios, SWR, RTK Query, plain useEffect)
- **API base configuration**: Where the base URL and auth headers are set up.
- **Key queries & mutations**: Group by domain. For each, note the endpoint and what triggers it.

### <Domain name (e.g. Orders)>
- `useOrders` — `GET /api/orders` — fetches paginated order list, triggered on OrderListPage mount
- `useCreateOrder` — `POST /api/orders` — mutation called on checkout form submit
[...]

- **Error handling**: How API errors are caught and surfaced (global error boundary, per-query callbacks, toast notifications, etc.).

---

## Notes for Developers

Anything a new developer should know that isn't obvious from the code: non-standard patterns,
important conventions, known gotchas, or areas of tech debt.
```

---

## General Principles

**Write for the next developer.** Someone intelligent but new to this specific codebase. What do they need to understand to be productive quickly?

**Respect TypeScript.** When types are already expressive, don't repeat them in prose — add context and meaning instead. A well-typed component with a one-line JSDoc is often better than a poorly-typed one with a wall of comments.

**Flag surprises.** If you spot something unusual — a component with an enormous number of responsibilities, a store slice that's doing something unexpected, a query with a very short stale time — mention it in a comment or in the spec's Notes section. You're a second pair of eyes, not just a transcriber.

**Be concise.** React apps can have hundreds of components. Good documentation is selective — it illuminates the non-obvious and skips the self-evident.

**When intent is unclear, ask.** If a component's purpose isn't inferrable from its code and context, it's better to ask the user than to guess and document it wrong.