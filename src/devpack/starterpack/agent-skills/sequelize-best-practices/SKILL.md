---
name: sequelize-best-practices
description: >
  Sequelize ORM best practices for Node.js applications. Contains 50+ rules across 8 categories,
  prioritized by impact to guide automated refactoring and code generation. Use this skill when
  writing, reviewing, or refactoring Sequelize models, queries, migrations, associations, or
  Express/Node.js API code that interacts with relational databases via Sequelize. Triggers on
  tasks involving Sequelize models, database queries, connection setup, eager loading, transactions,
  migrations, or performance optimization. Do NOT use for MongoDB/Mongoose, Prisma, TypeORM,
  Drizzle, or other non-Sequelize ORMs.
---

# Sequelize Best Practices

Comprehensive best practices guide for building production-ready Node.js applications with Sequelize ORM. Contains 50+ rules across 8 categories, prioritized by impact to guide automated refactoring, code review, and code generation.

For detailed rules with code examples, read `references/rules.md`.

## When to Apply

Reference these guidelines when:

- Defining or refactoring Sequelize models
- Writing database queries (finders, includes, raw queries)
- Setting up associations between models
- Implementing transactions for multi-step operations
- Configuring connection pools and database connections
- Writing or reviewing migrations and seeders
- Optimizing query performance or fixing N+1 problems
- Building Express/Node.js APIs backed by Sequelize

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
| --- | --- | --- | --- |
| 1 | Eliminating N+1 & Query Waterfalls | CRITICAL | `query-` |
| 2 | Security & Input Safety | CRITICAL | `security-` |
| 3 | Model Design & Definitions | HIGH | `model-` |
| 4 | Transactions & Data Integrity | HIGH | `transaction-` |
| 5 | Migrations & Schema Management | MEDIUM-HIGH | `migration-` |
| 6 | Connection & Pool Management | MEDIUM | `connection-` |
| 7 | Association Patterns | MEDIUM | `association-` |
| 8 | Code Organization & Architecture | LOW-MEDIUM | `architecture-` |

## Quick Reference

### 1. Eliminating N+1 & Query Waterfalls (CRITICAL)

- `query-eager-loading` - Use `include` to fetch related data in a single query instead of looping
- `query-select-attributes` - Specify `attributes` to avoid fetching unnecessary columns
- `query-avoid-overfetch` - Do not eagerly load associations you don't need
- `query-use-separate` - Use `separate: true` for large hasMany to avoid row explosion
- `query-pagination` - Always paginate large result sets with `limit` and `offset`
- `query-raw-for-complex` - Use raw queries for complex aggregations instead of chaining ORM methods
- `query-subqueries` - Use `subQuery: false` when appropriate for better JOIN performance
- `query-scopes-reuse` - Define scopes for commonly reused query logic
- `query-findAndCountAll` - Use `findAndCountAll` for paginated endpoints needing totals

### 2. Security & Input Safety (CRITICAL)

- `security-parameterized-queries` - Always use replacements or bind parameters in raw queries, never string concatenation
- `security-validate-input` - Use Sequelize model validations and constraints to reject bad data at the ORM layer
- `security-exclude-sensitive` - Use `defaultScope` to exclude sensitive fields like passwords from query results
- `security-mass-assignment` - Explicitly define `attributes` on `create`/`update` or use field allowlists to prevent mass assignment
- `security-env-credentials` - Store database credentials in environment variables, never in code
- `security-ssl-production` - Enable SSL/TLS for database connections in production
- `security-logging-off-production` - Disable SQL query logging in production

### 3. Model Design & Definitions (HIGH)

- `model-use-migrations` - Never use `sync({ force })` or `sync({ alter })` in production — use migrations
- `model-explicit-tablename` - Set `tableName` explicitly rather than relying on auto-pluralization
- `model-uuid-primary-keys` - Prefer UUIDs over auto-increment integers for primary keys in distributed systems
- `model-proper-datatypes` - Use the most specific DataType for each column (e.g., `DATEONLY` vs `DATE`, `ENUM` vs `STRING`)
- `model-virtual-fields` - Use `DataTypes.VIRTUAL` for computed fields instead of storing derived data
- `model-paranoid-soft-deletes` - Use `paranoid: true` for soft deletes when audit trails or recovery matter
- `model-validations` - Define validations on the model, not just at the controller layer
- `model-hooks-sparingly` - Use hooks for cross-cutting concerns (hashing passwords, normalizing data) but avoid complex business logic in hooks
- `model-no-public-class-fields` - When extending `Model`, use `declare` (TypeScript) or avoid public class fields that shadow Sequelize getters/setters
- `model-timestamps` - Keep `timestamps: true` (the default) for `createdAt`/`updatedAt` tracking
- `model-indexes` - Define indexes on frequently queried columns directly in the model or migration

### 4. Transactions & Data Integrity (HIGH)

- `transaction-managed` - Prefer managed transactions (callback style) over unmanaged to guarantee rollback on error
- `transaction-multi-step` - Wrap any multi-model create/update/delete in a transaction
- `transaction-pass-option` - Always pass `{ transaction: t }` to every query inside a transaction block
- `transaction-isolation` - Set appropriate isolation levels for concurrent operations
- `transaction-avoid-network` - Avoid network calls (HTTP requests, external APIs) inside transactions — they hold connections open
- `transaction-optimistic-locking` - Use `version: true` for optimistic locking when concurrent updates are expected

### 5. Migrations & Schema Management (MEDIUM-HIGH)

- `migration-never-sync-prod` - Use Sequelize CLI migrations, never `sequelize.sync()` in production
- `migration-reversible` - Always implement both `up` and `down` methods in migrations
- `migration-small-steps` - One logical change per migration (add column, create table, add index)
- `migration-seed-data` - Use seeders for initial/test data, not migrations
- `migration-sequelizerc` - Configure `.sequelizerc` to point at your project's directory structure
- `migration-test-down` - Test the `down` migration to ensure rollbacks work cleanly

### 6. Connection & Pool Management (MEDIUM)

- `connection-pool-sizing` - Configure pool `max`/`min` based on your concurrency and database limits
- `connection-pool-production` - Use larger pool sizes in production (e.g., `max: 20`) vs development (`max: 5`)
- `connection-acquire-timeout` - Set `acquire` timeout to fail fast rather than queue indefinitely
- `connection-idle-cleanup` - Configure `idle` timeout to release unused connections
- `connection-singleton` - Create one Sequelize instance per process — do not instantiate per-request
- `connection-retry` - Implement retry logic with `retry.max` for transient connection failures
- `connection-close-gracefully` - Call `sequelize.close()` on process shutdown to drain the pool cleanly

### 7. Association Patterns (MEDIUM)

- `association-both-sides` - Define associations on both sides (`hasMany` + `belongsTo`) for bidirectional access
- `association-aliases` - Use `as` aliases when a model has multiple associations to the same target
- `association-through-attrs` - In M:N relations, exclude junction table attributes with `through: { attributes: [] }` unless needed
- `association-onDelete-cascade` - Set `onDelete: 'CASCADE'` or `'SET NULL'` explicitly — don't rely on defaults
- `association-foreignKey-explicit` - Always specify `foreignKey` explicitly rather than relying on Sequelize's naming inference
- `association-lazy-vs-eager` - Default to lazy loading; use eager loading only when you know you need the related data

### 8. Code Organization & Architecture (LOW-MEDIUM)

- `architecture-layered` - Separate routes → controllers → services → models (don't query the database in route handlers)
- `architecture-model-index` - Use a centralized `models/index.js` to auto-load models and set up associations
- `architecture-error-handling` - Catch Sequelize-specific errors (`ValidationError`, `UniqueConstraintError`) and return appropriate HTTP status codes
- `architecture-env-config` - Use environment-based config (`development`, `test`, `production`) in `config/database.js`
- `architecture-custom-methods` - Put reusable query logic in class methods or scopes, not in controllers
- `architecture-logging` - Use a structured logger (not `console.log`) for SQL query logging in development

## How to Use

Read the full rules document for detailed explanations and code examples:

```
references/rules.md
```

Each rule contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references
