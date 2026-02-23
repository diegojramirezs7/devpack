---
name: express-best-practices
description: Express.js performance, security, and reliability best practices for production applications. This skill should be used when writing, reviewing, or refactoring Express.js code to ensure optimal patterns. Triggers on tasks involving Express routes, middleware, error handling, API design, security hardening, or performance optimization.
license: MIT
metadata:
  author: community
  version: "1.0.0"
  tags:
    - express
---

# Express.js Best Practices

Comprehensive best practices guide for Express.js applications in production. Contains 38 rules across 7 categories, prioritized by impact to guide automated code review, refactoring, and generation.

## When to Apply

Reference these guidelines when:

- Writing new Express.js routes, middleware, or API endpoints
- Reviewing Express.js code for performance, security, or reliability issues
- Refactoring existing Express.js applications
- Setting up error handling, logging, or input validation
- Configuring Express.js for production deployment
- Designing middleware chains or application structure

## Rule Categories by Priority

| Priority | Category              | Impact        | Prefix        |
| -------- | --------------------- | ------------- | ------------- |
| 1        | Security              | CRITICAL      | `security-`   |
| 2        | Error Handling        | CRITICAL      | `error-`      |
| 3        | Performance           | HIGH          | `perf-`       |
| 4        | Middleware            | HIGH          | `middleware-` |
| 5        | Logging & Monitoring  | MEDIUM-HIGH   | `logging-`    |
| 6        | Project Structure     | MEDIUM        | `structure-`  |
| 7        | Production Deployment | HIGH-CRITICAL | `deploy-`     |

## Quick Reference

### 1. Security (CRITICAL)

- `security-helmet` — Use Helmet to set security HTTP headers
- `security-disable-powered-by` — Disable X-Powered-By header to reduce fingerprinting
- `security-validate-input` — Validate and sanitize all user input with Zod/Joi
- `security-prevent-open-redirects` — Validate redirect URLs against an allowlist
- `security-secure-cookies` — Set secure, httpOnly, sameSite, and custom cookie name
- `security-rate-limit-auth` — Rate limit login/signup to prevent brute-force attacks
- `security-tls` — Use TLS in production; set trust proxy behind reverse proxies
- `security-audit-deps` — Regularly audit dependencies with npm audit

### 2. Error Handling (CRITICAL)

- `error-centralized-handler` — Use a single error-handling middleware at the end of the chain
- `error-custom-classes` — Create AppError classes with status, code, and isOperational flag
- `error-async-handling` — Handle async errors properly (Express 5 auto-propagation or asyncHandler wrapper)
- `error-404-catch-all` — Register a catch-all handler after all routes for proper 404 responses
- `error-process-level` — Handle uncaughtException and unhandledRejection; exit and let process manager restart
- `error-no-stack-in-prod` — Never expose stack traces in production responses

### 3. Performance (HIGH)

- `perf-node-env-production` — Set NODE_ENV=production for caching and optimized error messages
- `perf-compression` — Enable gzip/brotli compression (prefer at reverse proxy level)
- `perf-no-sync-functions` — Never use synchronous I/O functions; use async/await or fs.promises
- `perf-reverse-proxy` — Run Express behind Nginx/HAProxy for TLS, static files, load balancing
- `perf-cluster-mode` — Use cluster module or PM2 to utilize all CPU cores
- `perf-cache-expensive-ops` — Cache database queries and API calls with LRU or Redis
- `perf-streaming` — Stream large responses instead of buffering in memory

### 4. Middleware (HIGH)

- `middleware-ordering` — Order: security → parsing → enrichment → auth → routes → 404 → error handler
- `middleware-limit-body-size` — Set explicit limits on express.json() and express.urlencoded()
- `middleware-scoped-routers` — Use express.Router() to scope middleware to specific route groups
- `middleware-single-responsibility` — Keep each middleware focused on one concern

### 5. Logging & Monitoring (MEDIUM-HIGH)

- `logging-structured` — Use Pino or Winston for structured JSON logging; never console.log in production
- `logging-request-ids` — Assign correlation IDs to every request for distributed tracing
- `logging-request-metadata` — Log method, path, status code, and response time for every request
- `logging-health-checks` — Expose /health endpoint for load balancers and orchestrators

### 6. Project Structure (MEDIUM)

- `structure-separate-concerns` — Organize into controllers, services, models, middleware layers
- `structure-env-config` — Use environment variables (dotenv for dev); never hardcode secrets
- `structure-app-server-split` — Export app without .listen() for testability with supertest

### 7. Production Deployment (HIGH-CRITICAL)

- `deploy-process-manager` — Use PM2 or systemd; never run node directly in production
- `deploy-graceful-shutdown` — Stop accepting connections, finish in-flight requests, close DB, then exit
- `deploy-cors` — Configure CORS with explicit origin allowlist; never use wildcard with credentials
- `deploy-static-files` — Serve static files via Nginx/CDN; set long-lived cache headers
- `deploy-timeouts` — Set keepAliveTimeout and headersTimeout to prevent hanging connections
- `deploy-express-5` — Use Express 5 for automatic async error propagation when possible

## How to Use

Read the rules file for detailed explanations and code examples:

```
references/rules.md
```

Each rule contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references
