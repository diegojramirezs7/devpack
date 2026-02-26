# docs-documentation

**Category**: Documentation
**Priority**: HIGH
**Prefix**: `docs-`

---

## Why It Matters

Well-documented React code reduces onboarding time and prevents knowledge silos. Documentation should explain _why_ and _what_, not restate what TypeScript types already make clear. This rule covers both inline JSDoc for individual components/modules and project-level spec documents.

---

## Component Documentation (Inline JSDoc)

### Applies to

Components (`.tsx`, `.jsx`), custom hooks, Redux/Zustand store slices, React Query files, utilities, and type definition files.

### Process

1. **Read the file carefully** before writing documentation. Understand props, internal state, side effects, data fetching, and connections to global state.
2. **Add JSDoc comments** directly to the source file following these conventions:

**Components:**
- JSDoc block above the component function describing its purpose, where it's used, and anything non-obvious.
- `@param` for each prop — name, type, and short description. If TypeScript types are already self-explanatory, focus on _meaning_ instead of restating the type.
- Briefly note significant internal state with inline comments — keep it light.
- Document `useEffect` blocks with a short inline comment explaining _why_ the effect exists. Side effects are where bugs hide.

**Custom hooks:**
- JSDoc block describing what the hook does, what it returns, and caveats (e.g. "must be used inside a Redux Provider").
- `@param` for each argument.
- `@returns` describing the return shape, especially for objects with multiple fields.

**Redux slices / Zustand stores:**
- JSDoc on the store/slice explaining what domain state it owns.
- Comment on each action/reducer explaining what triggers it and what it changes.
- Document selectors with what they derive and any memoization in play.

**React Query files:**
- Document each query/mutation hook: endpoint, return value, and key options (stale time, enabled conditions).

### Incorrect

```tsx
const OrderList: React.FC<OrderListProps> = ({ userId, pageSize = 20 }) => {
  const filters = useAppSelector(selectOrderFilters);
  const { data, isLoading } = useOrders(userId, filters, pageSize);

  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => params.set(k, v));
    window.history.replaceState(null, '', `?${params}`);
  }, [filters]);

  // ... render
};
```

### Correct

```tsx
/**
 * Displays a paginated list of user orders with filtering by status.
 * Used on the Account page. Fetches data via React Query and reads
 * filter state from the orders Redux slice.
 */
const OrderList: React.FC<OrderListProps> = ({ userId, pageSize = 20 }) => {
  const filters = useAppSelector(selectOrderFilters);
  const { data, isLoading } = useOrders(userId, filters, pageSize);

  // Sync selected filters to URL params so the page is shareable
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => params.set(k, v));
    window.history.replaceState(null, '', `?${params}`);
  }, [filters]);

  // ... render
};
```

```tsx
/**
 * Fetches and caches the current user's profile data.
 * Automatically refetches when the auth token changes.
 *
 * @returns The user profile, loading state, and a refetch function.
 */
export function useUserProfile() {
```

### General Rules

- Don't over-document. If the code is clear, a one-liner is enough.
- Don't restate TypeScript types in prose when they're already explicit — add meaning, not noise.
- If something is genuinely confusing or non-standard, say so in the comment.

---

## App Spec Documentation (Project-Level)

### When to Use

When a project-level overview, spec, or architectural summary is needed for a React/Next.js app.

### Process

1. **Explore the project structure.** Identify the router setup, pages/routes, global state solution (Redux, Zustand, Context), data-fetching layer (React Query, SWR, plain fetch), and `package.json` for key dependencies.
2. **Read key files** (prioritize in this order):
   - Router configuration (where routes are defined)
   - Page-level components (components that map to routes)
   - Store setup: Redux root reducer / Zustand stores / Context providers
   - Shared API client or query configuration (QueryClient setup, Axios instance)
   - `package.json` for major dependencies and scripts
   - Environment config (`.env.example` or similar)
3. **Write `SPEC.md`** in the project root using this template:

```markdown
# <Project Name> — App Spec

> One-paragraph summary of what this application does and who it's for.

---

## Page & Route Structure

| Path          | Component         | Description                           | Auth Required |
| ------------- | ----------------- | ------------------------------------- | ------------- |
| `/`           | `HomePage`        | Landing page, shows summary dashboard | No            |
| `/login`      | `LoginPage`       | Email/password login form             | No            |
| `/orders/:id` | `OrderDetailPage` | Detail view for a single order        | Yes           |

Note any nested routing, layout wrappers, or dynamic route patterns.

---

## State Management Architecture

- **Solution in use**: (e.g. Redux Toolkit, Zustand, React Context, or a combination)
- **Store structure**: List the main slices/stores and what domain each owns.
- **Key patterns**: Middleware, custom selectors, derived state, persistence (e.g. redux-persist).

---

## API Calls & Data Flow

- **Data fetching approach**: (e.g. React Query with Axios, SWR, RTK Query, plain useEffect)
- **API base configuration**: Where the base URL and auth headers are set up.
- **Key queries & mutations**: Group by domain — endpoint and trigger.
- **Error handling**: How API errors are caught and surfaced (error boundary, per-query callbacks, toasts, etc.).

---

## Notes for Developers

Non-standard patterns, important conventions, known gotchas, or areas of tech debt.
```

---

## General Principles

- **Write for the next developer.** What does someone intelligent but new to this codebase need to be productive quickly?
- **Respect TypeScript.** When types are expressive, don't repeat them — add context and meaning instead.
- **Flag surprises.** Components with enormous responsibilities, unexpected store patterns, queries with very short stale times — mention them.
- **Be concise.** React apps can have hundreds of components. Good documentation is selective.
- **When intent is unclear, ask.** Don't guess and document incorrectly.