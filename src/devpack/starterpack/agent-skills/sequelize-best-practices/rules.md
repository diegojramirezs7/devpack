# Sequelize Best Practices — Rules Reference

Complete rules with code examples organized by priority category.

## Table of Contents

- [1. Eliminating N+1 & Query Waterfalls (CRITICAL)](#1-eliminating-n1--query-waterfalls-critical)
- [2. Security & Input Safety (CRITICAL)](#2-security--input-safety-critical)
- [3. Model Design & Definitions (HIGH)](#3-model-design--definitions-high)
- [4. Transactions & Data Integrity (HIGH)](#4-transactions--data-integrity-high)
- [5. Migrations & Schema Management (MEDIUM-HIGH)](#5-migrations--schema-management-medium-high)
- [6. Connection & Pool Management (MEDIUM)](#6-connection--pool-management-medium)
- [7. Association Patterns (MEDIUM)](#7-association-patterns-medium)
- [8. Code Organization & Architecture (LOW-MEDIUM)](#8-code-organization--architecture-low-medium)

---

## 1. Eliminating N+1 & Query Waterfalls (CRITICAL)

The N+1 problem is the single most common Sequelize performance killer. A loop that fires one query per record can turn a 10ms operation into a 2-second crawl. Fix these first — everything else is a rounding error by comparison.

### query-eager-loading

Use `include` to fetch related data in a single JOIN query instead of looping.

**Incorrect (N+1 — fires 1 + N queries):**

```javascript
const users = await User.findAll();
for (const user of users) {
  const posts = await Post.findAll({ where: { userId: user.id } });
  user.dataValues.posts = posts;
}
```

**Correct (single query with JOIN):**

```javascript
const users = await User.findAll({
  include: [{
    model: Post,
    as: 'posts',
  }],
});
```

If you need nested associations (users → posts → comments), chain the `include`:

```javascript
const users = await User.findAll({
  include: [{
    model: Post,
    as: 'posts',
    include: [{
      model: Comment,
      as: 'comments',
    }],
  }],
});
```

### query-select-attributes

Always specify `attributes` to fetch only the columns you need. Fetching every column wastes bandwidth, memory, and serialization time — especially when tables contain blobs or large text fields.

**Incorrect (fetches all columns including large text):**

```javascript
const posts = await Post.findAll({
  include: [{ model: User }],
});
```

**Correct (select only needed columns):**

```javascript
const posts = await Post.findAll({
  attributes: ['id', 'title', 'publishedAt'],
  include: [{
    model: User,
    as: 'author',
    attributes: ['id', 'firstName', 'lastName'],
  }],
});
```

### query-avoid-overfetch

Eager loading is powerful but not free. Including associations you don't use inflates your result set and slows the query. Only include what the current endpoint actually needs.

**Incorrect (loads everything for a simple list):**

```javascript
const users = await User.findAll({
  include: [
    { model: Post },
    { model: Profile },
    { model: Role },
    { model: AuditLog },
  ],
});
```

**Correct (load only what this endpoint needs):**

```javascript
const users = await User.findAll({
  attributes: ['id', 'email', 'firstName', 'role'],
});
```

### query-use-separate

When a parent has many children, a JOIN can produce a cartesian explosion (1 parent × 100 children = 100 rows for one parent). Use `separate: true` to fire a second `IN` query instead of a massive JOIN.

**Incorrect (JOIN row explosion with large hasMany):**

```javascript
const authors = await User.findAll({
  include: [{ model: Post }], // 5 authors × 200 posts each = 1000 rows
});
```

**Correct (separate query avoids explosion):**

```javascript
const authors = await User.findAll({
  include: [{
    model: Post,
    separate: true, // runs: SELECT * FROM posts WHERE authorId IN (1,2,3,4,5)
  }],
});
```

### query-pagination

Never return unbounded result sets. Always paginate with `limit` and `offset`, or use cursor-based pagination for large tables.

**Incorrect (returns every row):**

```javascript
const posts = await Post.findAll({ where: { status: 'published' } });
```

**Correct (paginated):**

```javascript
const page = parseInt(req.query.page) || 1;
const pageSize = parseInt(req.query.pageSize) || 20;

const { rows, count } = await Post.findAndCountAll({
  where: { status: 'published' },
  limit: pageSize,
  offset: (page - 1) * pageSize,
  order: [['publishedAt', 'DESC']],
});
```

### query-raw-for-complex

For complex aggregations, window functions, or CTEs, raw SQL is clearer and faster than chaining Sequelize methods. Use parameterized replacements to stay safe.

**Incorrect (awkward ORM contortion for aggregation):**

```javascript
const result = await Post.findAll({
  attributes: [
    [sequelize.fn('DATE_TRUNC', 'month', sequelize.col('published_at')), 'month'],
    [sequelize.fn('COUNT', '*'), 'post_count'],
    [sequelize.fn('AVG', sequelize.col('view_count')), 'avg_views'],
  ],
  group: [sequelize.fn('DATE_TRUNC', 'month', sequelize.col('published_at'))],
});
```

**Correct (raw query with replacements):**

```javascript
const [results] = await sequelize.query(`
  SELECT
    DATE_TRUNC('month', published_at) AS month,
    COUNT(*) AS post_count,
    AVG(view_count) AS avg_views
  FROM posts
  WHERE author_id = :authorId
    AND status = 'published'
  GROUP BY DATE_TRUNC('month', published_at)
  ORDER BY month DESC
  LIMIT 12
`, {
  replacements: { authorId },
  type: sequelize.QueryTypes.SELECT,
});
```

### query-scopes-reuse

Define scopes for query patterns that appear in multiple places. Scopes keep code DRY and make refactoring safer.

```javascript
const Post = sequelize.define('Post', { /* ... */ }, {
  scopes: {
    published: {
      where: { status: 'published', publishedAt: { [Op.ne]: null } },
    },
    recent: {
      order: [['publishedAt', 'DESC']],
      limit: 10,
    },
    byAuthor(authorId) {
      return { where: { authorId } };
    },
  },
});

// Usage — composable:
const posts = await Post.scope('published', 'recent').findAll();
const myPosts = await Post.scope('published', { method: ['byAuthor', userId] }).findAll();
```

### query-findAndCountAll

For paginated list endpoints, `findAndCountAll` returns both the rows and the total count in one call, which is more efficient than running `findAll` + `count` separately.

```javascript
const { rows: posts, count: total } = await Post.findAndCountAll({
  where: { status: 'published' },
  limit: 20,
  offset: 0,
  order: [['createdAt', 'DESC']],
  distinct: true, // important when using include to avoid inflated counts
});
```

---

## 2. Security & Input Safety (CRITICAL)

SQL injection through an ORM is embarrassing and entirely preventable. Sequelize parameterizes queries automatically, but raw queries and sloppy patterns can open holes.

### security-parameterized-queries

Never interpolate user input into raw SQL strings. Use `replacements` (named `:param`) or `bind` (`$1`).

**Incorrect (SQL injection vulnerability):**

```javascript
const users = await sequelize.query(
  `SELECT * FROM users WHERE name = '${req.query.name}'`
);
```

**Correct (parameterized):**

```javascript
const users = await sequelize.query(
  'SELECT * FROM users WHERE name = :name',
  {
    replacements: { name: req.query.name },
    type: sequelize.QueryTypes.SELECT,
  }
);
```

### security-validate-input

Define validations directly on the model. They run automatically before `create` and `update`, catching bad data before it ever reaches the database.

```javascript
email: {
  type: DataTypes.STRING,
  allowNull: false,
  unique: { msg: 'Email already registered' },
  validate: {
    isEmail: { msg: 'Must be a valid email address' },
    notEmpty: { msg: 'Email is required' },
  },
},
password: {
  type: DataTypes.STRING,
  allowNull: false,
  validate: {
    len: { args: [8, 128], msg: 'Password must be 8–128 characters' },
  },
},
```

### security-exclude-sensitive

Use `defaultScope` to strip sensitive fields from every query result unless you explicitly opt in.

```javascript
const User = sequelize.define('User', { /* ... */ }, {
  defaultScope: {
    attributes: { exclude: ['password', 'resetToken'] },
  },
  scopes: {
    withPassword: {
      attributes: {}, // includes everything
    },
  },
});

// Normal queries never return password:
const user = await User.findByPk(id);

// Login flow explicitly opts in:
const user = await User.scope('withPassword').findOne({ where: { email } });
```

### security-mass-assignment

Never pass `req.body` directly to `create` or `update`. Allowlist the fields you expect.

**Incorrect (user can inject `role: 'admin'`):**

```javascript
const user = await User.create(req.body);
```

**Correct (explicit allowlist):**

```javascript
const { firstName, lastName, email, password } = req.body;
const user = await User.create({ firstName, lastName, email, password });
```

### security-env-credentials

Store all database credentials in environment variables. Never commit them to source control.

```javascript
// config/database.js
module.exports = {
  production: {
    use_env_variable: 'DATABASE_URL',
    dialect: 'postgres',
    dialectOptions: {
      ssl: { require: true, rejectUnauthorized: false },
    },
    logging: false,
  },
};
```

### security-ssl-production

Always enable SSL for database connections in production, especially with cloud-hosted databases.

```javascript
dialectOptions: {
  ssl: {
    require: true,
    rejectUnauthorized: false, // or provide CA cert for strict verification
  },
},
```

### security-logging-off-production

SQL query logging is invaluable in development but should be disabled in production for performance and to avoid leaking sensitive data to logs.

```javascript
const sequelize = new Sequelize(process.env.DATABASE_URL, {
  logging: process.env.NODE_ENV === 'development' ? console.log : false,
});
```

---

## 3. Model Design & Definitions (HIGH)

Well-defined models are the backbone of a maintainable Sequelize codebase. Sloppy model definitions cause bugs that are painful to track down later.

### model-use-migrations

`sync({ force: true })` drops and recreates your tables. `sync({ alter: true })` can corrupt data. Both are fine for prototyping; neither belongs in production.

**Incorrect:**

```javascript
// app.js — runs on every deploy
await sequelize.sync({ alter: true });
```

**Correct:**

```bash
# Generate a migration
npx sequelize-cli migration:generate --name add-users-table

# Apply migrations
npx sequelize-cli db:migrate

# Roll back if needed
npx sequelize-cli db:migrate:undo
```

### model-explicit-tablename

Sequelize auto-pluralizes model names (`User` → `Users`). This is surprising for non-English words and legacy schemas. Set `tableName` explicitly.

```javascript
const User = sequelize.define('User', { /* ... */ }, {
  tableName: 'users', // explicit, no surprises
});
```

Or disable pluralization globally:

```javascript
const sequelize = new Sequelize(/* ... */, {
  define: { freezeTableName: true },
});
```

### model-uuid-primary-keys

Auto-increment IDs leak information (total row count, insertion order) and cause conflicts in distributed systems. UUIDs are safer defaults.

```javascript
id: {
  type: DataTypes.UUID,
  defaultValue: DataTypes.UUIDV4,
  primaryKey: true,
},
```

### model-proper-datatypes

Use the most specific type available. `STRING` with no length creates `VARCHAR(255)` — fine for names, wasteful for country codes, wrong for booleans.

```javascript
// Good: precise types
role: { type: DataTypes.ENUM('user', 'admin', 'moderator'), defaultValue: 'user' },
birthDate: { type: DataTypes.DATEONLY },      // date without time
price: { type: DataTypes.DECIMAL(10, 2) },    // exact decimal for currency
isActive: { type: DataTypes.BOOLEAN, defaultValue: true },
metadata: { type: DataTypes.JSONB },          // indexed JSON (Postgres)
```

### model-virtual-fields

Use `DataTypes.VIRTUAL` for computed fields instead of storing redundant data.

```javascript
fullName: {
  type: DataTypes.VIRTUAL,
  get() {
    return `${this.firstName} ${this.lastName}`;
  },
},
```

### model-paranoid-soft-deletes

When you need audit trails or the ability to recover deleted records, enable `paranoid` mode. It adds a `deletedAt` column and filters deleted records out of all default queries.

```javascript
const User = sequelize.define('User', { /* ... */ }, {
  paranoid: true, // adds deletedAt, excludes deleted from findAll
});

await user.destroy();          // sets deletedAt
await User.findAll();          // excludes soft-deleted
await User.findAll({ paranoid: false }); // includes soft-deleted
await user.restore();          // clears deletedAt
```

### model-hooks-sparingly

Hooks are great for cross-cutting concerns like hashing passwords or normalizing emails. Avoid putting business logic in hooks — it becomes invisible and hard to test.

**Good use of hooks:**

```javascript
User.beforeCreate(async (user) => {
  if (user.password) {
    user.password = await bcrypt.hash(user.password, 12);
  }
});

User.beforeCreate((user) => {
  user.email = user.email.toLowerCase().trim();
});
```

**Avoid: business logic hidden in a hook:**

```javascript
// Bad — hard to discover, test, or override
User.afterCreate(async (user) => {
  await sendWelcomeEmail(user.email);
  await createDefaultWorkspace(user.id);
  await notifyAdmins(user);
});
```

### model-no-public-class-fields

When using the class-based pattern, public class fields shadow Sequelize's getters and setters. In TypeScript, use `declare`.

**Incorrect:**

```typescript
class User extends Model {
  id; // shadows Sequelize getter — user.id returns undefined
}
```

**Correct (TypeScript):**

```typescript
class User extends Model {
  declare id: number; // 'declare' prevents runtime field emission
  declare email: string;
}
```

### model-indexes

Define indexes on columns that appear in `WHERE`, `ORDER BY`, or `JOIN` conditions. Indexes in the model definition stay in sync with the code (but should also be in migrations for production).

```javascript
const Post = sequelize.define('Post', { /* ... */ }, {
  indexes: [
    { unique: true, fields: ['slug'] },
    { fields: ['authorId', 'status'] },       // composite for common query
    { fields: ['publishedAt'], where: { status: 'published' } }, // partial index
  ],
});
```

---

## 4. Transactions & Data Integrity (HIGH)

Any operation that touches more than one table (or multiple rows that must be consistent) needs a transaction. Without one, a crash mid-operation leaves your data in a broken state.

### transaction-managed

Managed transactions (callback style) automatically commit on success and rollback on error. Unmanaged transactions require manual commit/rollback and are easy to leak.

**Incorrect (unmanaged — easy to forget rollback):**

```javascript
const t = await sequelize.transaction();
try {
  await User.create({ name: 'Alice' }, { transaction: t });
  await Profile.create({ userId: user.id }, { transaction: t });
  await t.commit();
} catch (err) {
  await t.rollback();
  throw err;
}
```

**Correct (managed — rollback is automatic):**

```javascript
await sequelize.transaction(async (t) => {
  const user = await User.create({ name: 'Alice' }, { transaction: t });
  await Profile.create({ userId: user.id }, { transaction: t });
});
```

### transaction-pass-option

Every query inside a transaction block must receive `{ transaction: t }`. Forgetting it means that query runs outside the transaction and won't be rolled back on failure.

```javascript
await sequelize.transaction(async (t) => {
  const user = await User.create({ name: 'Alice' }, { transaction: t });
  // WRONG: missing { transaction: t } — this runs outside the transaction
  // await Profile.create({ userId: user.id });
  // CORRECT:
  await Profile.create({ userId: user.id }, { transaction: t });
});
```

### transaction-avoid-network

Network calls inside a transaction hold a database connection open for the duration. If the external service is slow or down, your connection pool drains fast.

**Incorrect:**

```javascript
await sequelize.transaction(async (t) => {
  const order = await Order.create(data, { transaction: t });
  await callPaymentGateway(order); // slow external call holds connection
  await order.update({ status: 'paid' }, { transaction: t });
});
```

**Correct (network call outside transaction):**

```javascript
const order = await sequelize.transaction(async (t) => {
  return Order.create(data, { transaction: t });
});
const paymentResult = await callPaymentGateway(order);
await order.update({ status: paymentResult.success ? 'paid' : 'failed' });
```

### transaction-optimistic-locking

When concurrent updates are likely (e.g., multiple users editing the same record), optimistic locking prevents silent overwrites by checking a `version` column.

```javascript
const Product = sequelize.define('Product', {
  name: DataTypes.STRING,
  stock: DataTypes.INTEGER,
}, {
  version: true, // adds a `version` column, checked on update
});

// If another process updated the row since this read, the update throws OptimisticLockError
const product = await Product.findByPk(id);
product.stock -= 1;
await product.save(); // throws if version has changed
```

---

## 5. Migrations & Schema Management (MEDIUM-HIGH)

Migrations are the only safe way to evolve a production database schema. They provide a versioned, reversible history of every structural change.

### migration-never-sync-prod

`sequelize.sync()` compares the model to the database and issues DDL. In production, this can drop columns, delete data, or fail in unpredictable ways. Use migrations exclusively.

### migration-reversible

Always implement `down` so you can roll back a failed deploy. If the migration can't be reversed (e.g., dropping a column), document why.

```javascript
module.exports = {
  async up(queryInterface, Sequelize) {
    await queryInterface.addColumn('users', 'phoneNumber', {
      type: Sequelize.STRING(20),
      allowNull: true,
    });
  },

  async down(queryInterface) {
    await queryInterface.removeColumn('users', 'phoneNumber');
  },
};
```

### migration-small-steps

One logical change per migration. Combining "add column + create index + rename table" in a single migration makes rollbacks dangerous.

### migration-seed-data

Seeders populate initial or test data. Migrations change schema. Don't mix them.

```javascript
// seeders/20240101-demo-users.js
module.exports = {
  async up(queryInterface) {
    await queryInterface.bulkInsert('users', [
      { id: '...', firstName: 'Admin', email: 'admin@example.com', role: 'admin', createdAt: new Date(), updatedAt: new Date() },
    ]);
  },
  async down(queryInterface) {
    await queryInterface.bulkDelete('users', null, {});
  },
};
```

---

## 6. Connection & Pool Management (MEDIUM)

Sequelize maintains a pool of reusable database connections. Misconfigured pools cause either connection exhaustion (too small) or wasted resources (too large).

### connection-pool-sizing

The default pool size is 5. That's fine for development. In production, size the pool based on your expected concurrency and your database server's `max_connections`.

```javascript
// Development
pool: { max: 5, min: 0, acquire: 30000, idle: 10000 }

// Production
pool: { max: 20, min: 5, acquire: 60000, idle: 10000 }
```

Rule of thumb: `max` should not exceed your database's `max_connections` divided by the number of application instances.

### connection-singleton

Create one Sequelize instance per process. Instantiating Sequelize per-request creates a new pool each time and exhausts database connections.

**Incorrect:**

```javascript
app.get('/users', async (req, res) => {
  const sequelize = new Sequelize(/* ... */); // new pool per request!
  const users = await User.findAll();
  res.json(users);
});
```

**Correct:**

```javascript
// models/index.js — initialized once at startup
const sequelize = new Sequelize(/* ... */);
module.exports = { sequelize };
```

### connection-close-gracefully

On process shutdown (`SIGTERM`, `SIGINT`), drain the pool to avoid dropped queries.

```javascript
process.on('SIGTERM', async () => {
  console.log('Shutting down...');
  await sequelize.close();
  process.exit(0);
});
```

---

## 7. Association Patterns (MEDIUM)

Associations define how models relate. Getting them right means Sequelize can generate efficient JOINs and provide convenient accessor methods. Getting them wrong causes confusing runtime errors.

### association-both-sides

Always define both sides of a relationship. Without the inverse, Sequelize can't generate the correct JOINs or accessor methods from both directions.

```javascript
// models/user.model.js
User.associate = (models) => {
  User.hasMany(models.Post, { foreignKey: 'authorId', as: 'posts' });
};

// models/post.model.js
Post.associate = (models) => {
  Post.belongsTo(models.User, { foreignKey: 'authorId', as: 'author' });
};
```

### association-aliases

When a model has multiple associations to the same target, aliases are mandatory to disambiguate.

```javascript
Post.belongsTo(User, { as: 'author', foreignKey: 'authorId' });
Post.belongsTo(User, { as: 'editor', foreignKey: 'editorId' });

// Querying:
const post = await Post.findByPk(id, {
  include: [
    { model: User, as: 'author' },
    { model: User, as: 'editor' },
  ],
});
```

### association-through-attrs

In many-to-many relations, the junction table's attributes are usually noise. Exclude them by default and include them only when needed.

```javascript
const users = await User.findAll({
  include: [{
    model: Project,
    through: { attributes: [] }, // hides junction table columns
  }],
});

// When you need junction data (e.g., role):
const users = await User.findAll({
  include: [{
    model: Project,
    through: { attributes: ['role', 'joinedAt'] },
  }],
});
```

### association-foreignKey-explicit

Relying on Sequelize's auto-generated foreign key names is fragile and confusing. Specify them explicitly.

```javascript
// Explicit — clear, predictable
User.hasMany(Post, { foreignKey: 'authorId', as: 'posts' });
Post.belongsTo(User, { foreignKey: 'authorId', as: 'author' });
```

### association-onDelete-cascade

Set `onDelete` explicitly. The default varies by association type and can surprise you.

```javascript
User.hasMany(Post, {
  foreignKey: 'authorId',
  onDelete: 'CASCADE', // delete user → delete their posts
});

Post.belongsTo(Category, {
  foreignKey: 'categoryId',
  onDelete: 'SET NULL', // delete category → set posts.categoryId to null
});
```

---

## 8. Code Organization & Architecture (LOW-MEDIUM)

Clean architecture makes Sequelize applications easier to maintain, test, and scale. These patterns keep database concerns out of your route handlers and your business logic testable.

### architecture-layered

Separate your application into layers: routes → controllers → services → models. Each layer has a single responsibility.

```
routes/user.routes.js     → defines endpoints and middleware
controllers/user.ctrl.js  → parses request, calls service, formats response
services/user.service.js  → contains business logic, calls models
models/user.model.js      → defines schema, validations, hooks
```

**Incorrect (database query in route handler):**

```javascript
router.get('/users', async (req, res) => {
  const users = await User.findAll({ where: { isActive: true } });
  res.json(users);
});
```

**Correct (layered):**

```javascript
// routes/user.routes.js
router.get('/users', userController.list);

// controllers/user.controller.js
exports.list = async (req, res, next) => {
  try {
    const users = await userService.getActiveUsers(req.query);
    res.json({ data: users });
  } catch (err) {
    next(err);
  }
};

// services/user.service.js
exports.getActiveUsers = async ({ page = 1, pageSize = 20 }) => {
  return User.scope('active').findAndCountAll({
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });
};
```

### architecture-model-index

Use a centralized `models/index.js` that auto-discovers model files, initializes them, and calls their `associate` methods. This keeps model registration out of your application entry point.

```javascript
// models/index.js
const fs = require('fs');
const path = require('path');
const { Sequelize } = require('sequelize');
const config = require('../config/database')[process.env.NODE_ENV || 'development'];

const sequelize = config.use_env_variable
  ? new Sequelize(process.env[config.use_env_variable], config)
  : new Sequelize(config.database, config.username, config.password, config);

const db = {};

fs.readdirSync(__dirname)
  .filter(f => f !== 'index.js' && f.endsWith('.js'))
  .forEach(file => {
    const model = require(path.join(__dirname, file))(sequelize, Sequelize.DataTypes);
    db[model.name] = model;
  });

Object.values(db).forEach(model => {
  if (model.associate) model.associate(db);
});

db.sequelize = sequelize;
module.exports = db;
```

### architecture-error-handling

Catch Sequelize-specific errors and translate them to appropriate HTTP responses. Generic 500s for validation failures frustrate API consumers.

```javascript
const { ValidationError, UniqueConstraintError, ForeignKeyConstraintError } = require('sequelize');

app.use((err, req, res, next) => {
  if (err instanceof UniqueConstraintError) {
    return res.status(409).json({
      error: 'Conflict',
      message: 'A record with that value already exists',
      fields: err.fields,
    });
  }

  if (err instanceof ValidationError) {
    return res.status(400).json({
      error: 'Validation Error',
      messages: err.errors.map(e => ({ field: e.path, message: e.message })),
    });
  }

  if (err instanceof ForeignKeyConstraintError) {
    return res.status(400).json({
      error: 'Invalid Reference',
      message: 'Referenced record does not exist',
    });
  }

  console.error(err);
  res.status(500).json({ error: 'Internal Server Error' });
});
```

### architecture-env-config

Support multiple environments in your database configuration. Use `use_env_variable` for production so credentials come from the environment, not your config file.

```javascript
// config/database.js
module.exports = {
  development: {
    username: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'app_dev',
    host: '127.0.0.1',
    dialect: 'postgres',
    logging: console.log,
    pool: { max: 5, min: 0, acquire: 30000, idle: 10000 },
  },
  test: {
    username: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'app_test',
    host: '127.0.0.1',
    dialect: 'postgres',
    logging: false,
  },
  production: {
    use_env_variable: 'DATABASE_URL',
    dialect: 'postgres',
    dialectOptions: { ssl: { require: true, rejectUnauthorized: false } },
    logging: false,
    pool: { max: 20, min: 5, acquire: 60000, idle: 10000 },
  },
};
```

### architecture-custom-methods

Encapsulate reusable query logic as static methods or scopes on the model, not in controllers.

```javascript
// On the model
class Post extends Model {
  static async findPublishedByAuthor(authorId, { page = 1, pageSize = 20 } = {}) {
    return this.findAndCountAll({
      where: { authorId, status: 'published' },
      order: [['publishedAt', 'DESC']],
      limit: pageSize,
      offset: (page - 1) * pageSize,
      distinct: true,
    });
  }
}

// In the service — clean and declarative
const posts = await Post.findPublishedByAuthor(userId, { page: 2 });
```
