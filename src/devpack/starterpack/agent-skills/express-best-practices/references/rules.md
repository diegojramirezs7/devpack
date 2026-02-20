# Express.js Best Practices — Full Rules

Detailed explanations and code examples for all 38 rules. Organized by category and priority.

Sources: [Express.js Performance Guide](https://expressjs.com/en/advanced/best-practice-performance.html), [Express.js Security Guide](https://expressjs.com/en/advanced/best-practice-security.html), [Sematext Express.js Best Practices](https://sematext.com/blog/expressjs-best-practices/).

---

## 1. Security (CRITICAL)

---

### `security-helmet`

Use Helmet to set security HTTP headers.

**Impact: CRITICAL**
**Tags:** security, headers, helmet, xss, clickjacking

Helmet sets Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, and other headers that protect against well-known web vulnerabilities including XSS, clickjacking, and MIME sniffing.

**Incorrect (no security headers):**

```javascript
const express = require('express');
const app = express();

// No security headers — vulnerable to clickjacking, XSS, MIME sniffing
app.get('/', (req, res) => {
  res.send('Hello');
});
```

**Correct:**

```javascript
const express = require('express');
const helmet = require('helmet');
const app = express();

app.use(helmet());

app.get('/', (req, res) => {
  res.send('Hello');
});
```

---

### `security-disable-powered-by`

Disable the X-Powered-By header to reduce fingerprinting.

**Impact: HIGH**
**Tags:** security, fingerprinting, headers

The default `X-Powered-By: Express` header reveals your stack, making it easier for attackers to target known Express vulnerabilities. Helmet disables this automatically, but if you are not using Helmet, disable it manually.

**Incorrect:**

```javascript
const app = express();
// X-Powered-By: Express is sent by default
```

**Correct:**

```javascript
const app = express();
app.disable('x-powered-by');
```

---

### `security-validate-input`

Validate and sanitize all user input with Zod, Joi, or express-validator.

**Impact: CRITICAL**
**Tags:** security, validation, injection, zod, joi, express-validator

Never trust user input. Use a validation library to check `req.body`, `req.params`, and `req.query` as early as possible in the middleware chain. This prevents injection attacks, crashes from malformed data, and unexpected behavior.

**Incorrect (no validation):**

```javascript
app.post('/users', async (req, res) => {
  // Directly using unvalidated input
  const user = await db.createUser(req.body);
  res.json(user);
});
```

**Correct (Zod with reusable middleware):**

```javascript
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
});

function validate(schema) {
  return (req, res, next) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (err) {
      next(err);
    }
  };
}

app.post('/users', validate(createUserSchema), async (req, res, next) => {
  const user = await db.createUser(req.body);
  res.status(201).json(user);
});
```

---

### `security-prevent-open-redirects`

Validate redirect URLs against an allowlist.

**Impact: HIGH**
**Tags:** security, redirect, phishing, validation

When using user-supplied URLs for redirects, always validate the target. Open redirects can be exploited for phishing.

**Incorrect:**

```javascript
app.get('/redirect', (req, res) => {
  res.redirect(req.query.url); // User controls redirect target
});
```

**Correct:**

```javascript
const ALLOWED_HOSTS = ['example.com', 'app.example.com'];

app.get('/redirect', (req, res) => {
  try {
    const target = new URL(req.query.url);
    if (!ALLOWED_HOSTS.includes(target.host)) {
      return res.status(400).send('Redirect not allowed');
    }
    res.redirect(target.href);
  } catch {
    res.status(400).send('Invalid URL');
  }
});
```

---

### `security-secure-cookies`

Set secure, httpOnly, sameSite, and a custom cookie name.

**Impact: HIGH**
**Tags:** security, cookies, session, xss

Default session cookie names (`connect.sid`) reveal your stack. Missing security flags leave cookies vulnerable to interception and XSS.

**Incorrect:**

```javascript
app.use(session({
  secret: 'keyboard cat',
  // Default name, no secure flags
}));
```

**Correct:**

```javascript
const session = require('express-session');

app.set('trust proxy', 1);
app.use(session({
  secret: process.env.SESSION_SECRET,
  name: 'sessionId',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,
    httpOnly: true,
    sameSite: 'strict',
    maxAge: 60 * 60 * 1000, // 1 hour
  },
}));
```

---

### `security-rate-limit-auth`

Rate limit login and signup endpoints to prevent brute-force attacks.

**Impact: HIGH**
**Tags:** security, rate-limiting, brute-force, authentication

**Incorrect:**

```javascript
app.post('/login', async (req, res) => {
  // No rate limiting — brute-force vulnerable
  const user = await authenticate(req.body.email, req.body.password);
  res.json({ token: generateToken(user) });
});
```

**Correct:**

```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many login attempts, please try again later' },
});

app.post('/login', loginLimiter, async (req, res, next) => {
  try {
    const user = await authenticate(req.body.email, req.body.password);
    res.json({ token: generateToken(user) });
  } catch (err) {
    next(err);
  }
});
```

---

### `security-tls`

Use TLS in production; set trust proxy behind reverse proxies.

**Impact: CRITICAL**
**Tags:** security, tls, https, proxy

All production traffic must be encrypted. Use a reverse proxy (Nginx, Cloudflare) to terminate TLS and configure `trust proxy` so Express respects `X-Forwarded-*` headers.

**Correct:**

```javascript
app.set('trust proxy', 1);

// Redirect HTTP to HTTPS if not handled by proxy
app.use((req, res, next) => {
  if (req.secure || req.headers['x-forwarded-proto'] === 'https') {
    return next();
  }
  res.redirect(301, `https://${req.headers.host}${req.url}`);
});
```

---

### `security-audit-deps`

Regularly audit dependencies with npm audit.

**Impact: HIGH**
**Tags:** security, dependencies, npm-audit, vulnerabilities

Outdated dependencies are one of the most common attack vectors. Audit regularly and automate in CI.

**Correct:**

```bash
npm audit
npm audit fix
npm outdated
```

---

## 2. Error Handling (CRITICAL)

---

### `error-centralized-handler`

Use a single error-handling middleware at the end of the chain.

**Impact: CRITICAL**
**Tags:** error-handling, middleware, centralized, production

Express recognizes error handlers by their 4-argument signature `(err, req, res, next)`. Define one centralized handler instead of scattering `res.status(500)` calls throughout routes.

**Incorrect (scattered error handling):**

```javascript
app.get('/users/:id', async (req, res) => {
  try {
    const user = await db.findUser(req.params.id);
    if (!user) return res.status(404).json({ error: 'Not found' });
    res.json(user);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

**Correct:**

```javascript
// Routes — thin, delegate errors
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  if (!user) throw new AppError('User not found', 404);
  res.json(user);
});

// Centralized error handler — registered last
app.use((err, req, res, next) => {
  const status = err.status || 500;
  const message = err.isOperational ? err.message : 'Internal server error';

  logger.error({ err, requestId: req.id, path: req.path });

  res.status(status).json({
    success: false,
    error: { code: err.code || 'INTERNAL_ERROR', message },
  });
});
```

---

### `error-custom-classes`

Create AppError classes with status, code, and isOperational flag.

**Impact: HIGH**
**Tags:** error-handling, custom-errors, operational-errors

Custom error classes distinguish expected operational errors (bad input, not found) from programmer bugs, enabling different handling strategies.

**Correct:**

```javascript
class AppError extends Error {
  constructor(message, status = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.name = this.constructor.name;
    this.status = status;
    this.code = code;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

class ValidationError extends AppError {
  constructor(details) {
    super('Validation failed', 422, 'VALIDATION_ERROR');
    this.details = details;
  }
}
```

---

### `error-async-handling`

Handle async errors properly.

**Impact: CRITICAL**
**Tags:** error-handling, async, promises, express-5, express-4

In Express 5, async route handlers automatically propagate rejected promises to error middleware. In Express 4, unhandled promise rejections crash the process — use a wrapper.

**Incorrect (Express 4 — unhandled rejection crashes server):**

```javascript
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id); // if this rejects, crash
  res.json(user);
});
```

**Correct (Express 5 — automatic propagation):**

```javascript
// Express 5: rejected promises automatically call next(err)
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  res.json(user);
});
```

**Correct (Express 4 — asyncHandler wrapper):**

```javascript
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await db.findUser(req.params.id);
  res.json(user);
}));
```

---

### `error-404-catch-all`

Register a catch-all handler after all routes for proper 404 responses.

**Impact: MEDIUM**
**Tags:** error-handling, 404, routing

Prevents Express from returning its default HTML 404 page.

**Correct:**

```javascript
// After all other routes
app.use((req, res, next) => {
  next(new AppError(`Cannot ${req.method} ${req.originalUrl}`, 404, 'NOT_FOUND'));
});

// Then the centralized error handler
app.use(errorHandler);
```

---

### `error-process-level`

Handle uncaughtException and unhandledRejection at the process level.

**Impact: HIGH**
**Tags:** error-handling, process, crash, graceful-shutdown

Log the error and exit gracefully. Do not attempt to continue serving requests in an unknown state. Use a process manager to auto-restart.

**Correct:**

```javascript
process.on('uncaughtException', (err) => {
  logger.fatal({ err }, 'Uncaught exception — shutting down');
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logger.fatal({ err: reason }, 'Unhandled rejection — shutting down');
  process.exit(1);
});
```

---

### `error-no-stack-in-prod`

Never expose stack traces in production responses.

**Impact: HIGH**
**Tags:** error-handling, security, stack-trace, production

Stack traces reveal internal file paths, dependency versions, and code structure. Only include them in development.

**Correct:**

```javascript
app.use((err, req, res, next) => {
  const status = err.status || 500;
  const response = {
    success: false,
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message: err.isOperational ? err.message : 'Internal server error',
    },
  };

  if (process.env.NODE_ENV !== 'production') {
    response.error.stack = err.stack;
  }

  res.status(status).json(response);
});
```

---

## 3. Performance (HIGH)

---

### `perf-node-env-production`

Set NODE_ENV=production.

**Impact: CRITICAL**
**Tags:** performance, environment, production, caching

Enables view template caching, CSS caching, and less verbose error messages. Can improve performance by up to 3x.

**Incorrect:**

```bash
# NODE_ENV not set — runs in development mode with no caching
node server.js
```

**Correct:**

```bash
NODE_ENV=production node server.js
```

Or in systemd:

```ini
[Service]
Environment=NODE_ENV=production
```

---

### `perf-compression`

Enable gzip/brotli compression.

**Impact: HIGH**
**Tags:** performance, compression, gzip, brotli, nginx

Compress response bodies to significantly reduce transfer size. For high-traffic apps, prefer handling compression at the reverse proxy level to free Node.js CPU for application logic.

**Correct (application-level):**

```javascript
const compression = require('compression');
app.use(compression());
```

**Correct (Nginx — preferred for high traffic):**

```nginx
gzip on;
gzip_types text/plain application/json application/javascript text/css;
gzip_min_length 1000;
```

---

### `perf-no-sync-functions`

Never use synchronous I/O functions.

**Impact: CRITICAL**
**Tags:** performance, async, event-loop, blocking

Synchronous functions block the event loop, stalling all concurrent requests. Always use async versions. Use `--trace-sync-io` during development to detect violations.

**Incorrect:**

```javascript
app.get('/config', (req, res) => {
  const data = fs.readFileSync('/path/to/config.json', 'utf8');
  res.json(JSON.parse(data));
});
```

**Correct:**

```javascript
app.get('/config', async (req, res) => {
  const data = await fs.promises.readFile('/path/to/config.json', 'utf8');
  res.json(JSON.parse(data));
});
```

---

### `perf-reverse-proxy`

Run Express behind a reverse proxy (Nginx, HAProxy, Caddy).

**Impact: HIGH**
**Tags:** performance, nginx, reverse-proxy, load-balancing, production

The reverse proxy handles TLS termination, static file serving, compression, load balancing, and response caching — freeing Express for application logic.

**Correct (Nginx config):**

```nginx
upstream express_app {
  server 127.0.0.1:3000;
  server 127.0.0.1:3001;
}

server {
  listen 443 ssl;
  server_name example.com;

  location / {
    proxy_pass http://express_app;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
  }
}
```

---

### `perf-cluster-mode`

Use cluster module or PM2 to utilize all CPU cores.

**Impact: HIGH**
**Tags:** performance, cluster, pm2, scaling, multi-core

A single Node.js process uses one CPU core. Spawn one worker per core to distribute load. Clustered processes do not share memory — use Redis or a database for shared state.

**Correct (cluster module):**

```javascript
const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  const cpuCount = os.cpus().length;
  for (let i = 0; i < cpuCount; i++) {
    cluster.fork();
  }
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died, respawning`);
    cluster.fork();
  });
} else {
  const app = require('./app');
  app.listen(3000);
}
```

**Correct (PM2):**

```bash
pm2 start app.js -i max --name my-app
```

---

### `perf-cache-expensive-ops`

Cache database queries and API calls with LRU or Redis.

**Impact: MEDIUM**
**Tags:** performance, caching, lru, redis, database

Use in-memory LRU caches for single-instance apps, or Redis for multi-instance deployments.

**Correct:**

```javascript
const { LRUCache } = require('lru-cache');

const userCache = new LRUCache({
  max: 500,
  ttl: 5 * 60 * 1000, // 5 minutes
});

app.get('/users/:id', async (req, res) => {
  const { id } = req.params;
  const cached = userCache.get(id);
  if (cached) return res.json(cached);

  const user = await db.findUser(id);
  if (!user) throw new NotFoundError('User');

  userCache.set(id, user);
  res.json(user);
});
```

---

### `perf-streaming`

Stream large responses instead of buffering in memory.

**Impact: MEDIUM**
**Tags:** performance, streaming, memory, large-data

For large datasets or file downloads, stream the response to keep memory usage constant regardless of payload size.

**Incorrect:**

```javascript
app.get('/export', async (req, res) => {
  const data = await db.getAllRecords(); // loads everything into memory
  res.json(data);
});
```

**Correct:**

```javascript
app.get('/export', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  const stream = db.getAllRecordsStream();
  stream.pipe(res);
  stream.on('error', (err) => {
    res.destroy();
    logger.error({ err }, 'Stream error during export');
  });
});
```

---

## 4. Middleware (HIGH)

---

### `middleware-ordering`

Order middleware correctly: security → parsing → enrichment → auth → routes → 404 → error handler.

**Impact: HIGH**
**Tags:** middleware, ordering, architecture, security

Middleware order matters. Security and parsing must run before routes; error handlers must be last.

**Correct:**

```javascript
// 1. Security
app.use(helmet());
app.use(cors(corsOptions));

// 2. Request parsing
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// 3. Request enrichment
app.use(requestId());
app.use(requestLogger);

// 4. Authentication
app.use('/api', authMiddleware);

// 5. Routes
app.use('/api/users', usersRouter);
app.use('/api/posts', postsRouter);

// 6. 404 handler
app.use(notFoundHandler);

// 7. Error handler (always last)
app.use(errorHandler);
```

---

### `middleware-limit-body-size`

Set explicit limits on express.json() and express.urlencoded().

**Impact: HIGH**
**Tags:** middleware, security, dos, body-parser, payload

Prevents denial-of-service attacks via oversized payloads. Apply higher limits selectively on routes that need them.

**Incorrect:**

```javascript
app.use(express.json()); // default 100kb may be too generous
```

**Correct:**

```javascript
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true, limit: '10kb' }));

// Selectively higher for upload routes
app.post('/upload', express.json({ limit: '5mb' }), uploadHandler);
```

---

### `middleware-scoped-routers`

Use express.Router() to scope middleware to specific route groups.

**Impact: MEDIUM**
**Tags:** middleware, router, scoping, authentication, architecture

Apply middleware only where needed instead of globally. This avoids running auth middleware on public endpoints like health checks.

**Incorrect:**

```javascript
app.use(authMiddleware); // applies to ALL routes including /health
app.get('/health', healthCheck);
app.get('/api/users', getUsers);
```

**Correct:**

```javascript
const publicRouter = express.Router();
publicRouter.get('/health', healthCheck);
publicRouter.get('/docs', serveDocs);

const apiRouter = express.Router();
apiRouter.use(authMiddleware);
apiRouter.get('/users', getUsers);
apiRouter.get('/posts', getPosts);

app.use(publicRouter);
app.use('/api', apiRouter);
```

---

### `middleware-single-responsibility`

Keep each middleware focused on one concern.

**Impact: MEDIUM**
**Tags:** middleware, single-responsibility, composition, clean-code

Avoid combining authentication, logging, validation, and business logic in a single function. Compose small, focused middleware instead.

**Incorrect:**

```javascript
app.post('/users', (req, res, next) => {
  if (!req.headers.authorization) return res.status(401).send('No auth');
  if (!req.body.email) return res.status(400).send('No email');
  console.log('Creating user:', req.body.email);
  next();
}, createUser);
```

**Correct:**

```javascript
app.post('/users',
  authenticate,
  validate(createUserSchema),
  logAction('create_user'),
  createUser
);
```

---

## 5. Logging & Monitoring (MEDIUM-HIGH)

---

### `logging-structured`

Use Pino or Winston for structured JSON logging; never console.log in production.

**Impact: HIGH**
**Tags:** logging, pino, winston, structured, production

`console.log()` and `console.error()` are synchronous when the destination is a terminal or file and lack structure for querying. Use a proper logging library.

**Incorrect:**

```javascript
app.get('/users/:id', async (req, res) => {
  console.log('Fetching user', req.params.id);
  const user = await db.findUser(req.params.id);
  res.json(user);
});
```

**Correct:**

```javascript
const pino = require('pino');
const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

app.get('/users/:id', async (req, res) => {
  logger.info({ userId: req.params.id }, 'Fetching user');
  const user = await db.findUser(req.params.id);
  res.json(user);
});
```

---

### `logging-request-ids`

Assign correlation IDs to every request for distributed tracing.

**Impact: MEDIUM**
**Tags:** logging, tracing, request-id, observability

A unique ID per request makes it possible to trace a single request across middleware, services, and error handlers.

**Correct:**

```javascript
const { randomUUID } = require('crypto');

app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || randomUUID();
  res.setHeader('x-request-id', req.id);
  next();
});
```

---

### `logging-request-metadata`

Log method, path, status code, and response time for every request.

**Impact: MEDIUM**
**Tags:** logging, request-logging, observability, pino-http

Use `pino-http` or equivalent to automatically log request metadata with appropriate log levels.

**Correct:**

```javascript
const pinoHttp = require('pino-http');

app.use(pinoHttp({
  logger,
  customLogLevel: (req, res, err) => {
    if (res.statusCode >= 500 || err) return 'error';
    if (res.statusCode >= 400) return 'warn';
    return 'info';
  },
}));
```

---

### `logging-health-checks`

Expose a /health endpoint for load balancers and orchestrators.

**Impact: HIGH**
**Tags:** monitoring, health-check, load-balancer, kubernetes, production

Load balancers and container orchestrators use health endpoints to route traffic and restart unhealthy instances.

**Correct:**

```javascript
app.get('/health', async (req, res) => {
  const checks = {
    uptime: process.uptime(),
    status: 'ok',
    timestamp: Date.now(),
  };

  try {
    await db.ping();
    checks.database = 'ok';
  } catch {
    checks.database = 'error';
    checks.status = 'degraded';
  }

  const statusCode = checks.status === 'ok' ? 200 : 503;
  res.status(statusCode).json(checks);
});
```

---

## 6. Project Structure (MEDIUM)

---

### `structure-separate-concerns`

Organize into controllers, services, models, and middleware layers.

**Impact: HIGH**
**Tags:** architecture, structure, separation-of-concerns, maintainability

Keep route handlers thin. Never put business logic or database queries directly in route files. Keep files under ~100 lines.

**Correct structure:**

```
src/
  config/          # Environment config, database config
  controllers/     # Route handlers — thin, call services
  services/        # Business logic
  models/          # Database models/queries
  middleware/      # Auth, validation, error handling, logging
  routes/          # Route definitions grouped by resource
  utils/           # Shared utilities
  app.js           # Express app setup (middleware + routes)
server.js          # Listen on port (separate from app for testing)
```

**Correct (thin controller):**

```javascript
// controllers/users.js
const userService = require('../services/userService');

exports.createUser = async (req, res) => {
  const user = await userService.create(req.body);
  res.status(201).json(user);
};
```

---

### `structure-env-config`

Use environment variables for configuration; never hardcode secrets.

**Impact: HIGH**
**Tags:** configuration, environment, dotenv, secrets, security

Use `dotenv` for local development and real environment variables in production. Never commit `.env` files.

**Incorrect:**

```javascript
const db = require('mysql').createConnection({
  host: 'prod-db.example.com',
  password: 'super_secret_123',
});
```

**Correct:**

```javascript
// config/index.js
require('dotenv').config(); // only loads in development

module.exports = {
  port: parseInt(process.env.PORT, 10) || 3000,
  db: {
    host: process.env.DB_HOST,
    password: process.env.DB_PASSWORD,
  },
  nodeEnv: process.env.NODE_ENV || 'development',
};
```

---

### `structure-app-server-split`

Export app without .listen() for testability.

**Impact: MEDIUM**
**Tags:** architecture, testing, supertest, separation

Separating app definition from server startup allows importing the app in tests without starting a real server.

**Correct:**

```javascript
// app.js
const express = require('express');
const app = express();
// ... middleware, routes, error handlers
module.exports = app;

// server.js
const app = require('./app');
const config = require('./config');
app.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
});

// test/users.test.js
const request = require('supertest');
const app = require('../app');

test('GET /users returns 200', async () => {
  const res = await request(app).get('/users');
  expect(res.status).toBe(200);
});
```

---

## 7. Production Deployment (HIGH-CRITICAL)

---

### `deploy-process-manager`

Use PM2 or systemd; never run node directly in production.

**Impact: CRITICAL**
**Tags:** deployment, pm2, systemd, process-manager, crash-recovery

A process manager automatically restarts your app on crashes, manages logs, and enables cluster mode.

**Correct (PM2):**

```bash
pm2 start server.js -i max --name my-app
pm2 save
pm2 startup
```

**Correct (systemd):**

```ini
[Unit]
Description=My Express App

[Service]
Type=simple
ExecStart=/usr/local/bin/node /app/server.js
WorkingDirectory=/app
User=nobody
Group=nogroup
Environment=NODE_ENV=production
Restart=always
RestartSec=5
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
```

---

### `deploy-graceful-shutdown`

Stop accepting connections, finish in-flight requests, close DB, then exit.

**Impact: HIGH**
**Tags:** deployment, graceful-shutdown, sigterm, zero-downtime

Prevents dropped requests during deployments and restarts.

**Correct:**

```javascript
const server = app.listen(config.port);

function gracefulShutdown(signal) {
  logger.info({ signal }, 'Shutdown signal received');

  server.close(async () => {
    logger.info('HTTP server closed');

    try {
      await db.disconnect();
      logger.info('Database connection closed');
    } catch (err) {
      logger.error({ err }, 'Error during database disconnect');
    }

    process.exit(0);
  });

  // Force shutdown after timeout
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30_000);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
```

---

### `deploy-cors`

Configure CORS with an explicit origin allowlist.

**Impact: HIGH**
**Tags:** deployment, cors, security, production

Never use `origin: '*'` with credentials. Never blindly reflect the request's Origin header.

**Incorrect:**

```javascript
app.use(cors()); // allows ALL origins
```

**Correct:**

```javascript
const cors = require('cors');

const ALLOWED_ORIGINS = [
  'https://app.example.com',
  'https://admin.example.com',
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

---

### `deploy-static-files`

Serve static files via Nginx/CDN; set long-lived cache headers.

**Impact: MEDIUM**
**Tags:** deployment, static-files, caching, nginx, cdn

In production, prefer serving static files through Nginx or a CDN instead of Express. If you must use Express, set proper cache headers.

**Correct (Express fallback):**

```javascript
app.use(express.static('public', {
  maxAge: '1y',
  etag: true,
  lastModified: true,
  immutable: true,
}));
```

**Correct (Nginx — preferred):**

```nginx
location /static/ {
  alias /app/public/;
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

---

### `deploy-timeouts`

Set keepAliveTimeout and headersTimeout to prevent hanging connections.

**Impact: MEDIUM**
**Tags:** deployment, timeouts, keep-alive, connections, production

Set `keepAliveTimeout` higher than your load balancer's timeout (typically 60s) to prevent premature connection drops.

**Correct:**

```javascript
const server = app.listen(config.port);

server.keepAliveTimeout = 65_000;  // must be > load balancer timeout
server.headersTimeout = 66_000;
server.timeout = 30_000;           // optional request timeout
```

---

### `deploy-express-5`

Use Express 5 for automatic async error propagation when possible.

**Impact: MEDIUM**
**Tags:** express-5, async, error-handling, migration

Express 5 automatically forwards rejected promises in route handlers to error middleware, eliminating the need for `asyncHandler` wrappers.

**Express 4 (requires wrapper):**

```javascript
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

app.get('/data', asyncHandler(async (req, res) => {
  const data = await fetchData();
  res.json(data);
}));
```

**Express 5 (automatic):**

```javascript
// Rejected promises automatically call next(err)
app.get('/data', async (req, res) => {
  const data = await fetchData();
  res.json(data);
});
```