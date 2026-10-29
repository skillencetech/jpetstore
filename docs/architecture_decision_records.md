# Architecture Decision Records (ADR)
## Project: JPetStore 6 AI-Native Modernization

**Status:** Approved & Baselined  
**Role:** AI Technical Lead  
**Evaluation Standard:** docs/ASSESSMENT.pdf  
**Parent Roadmap:** docs/jpetstore_migration_proposal_and_roadmap.md  
**Baseline Architecture:** docs/jpetstore_architecture_decomposition.md  

---

### Index of Architecture Decisions

* [ADR-001: Target Web Framework Selection (FastAPI + Uvicorn ASGI)](#adr-001-target-web-framework-selection-fastapi--uvicorn-asgi)
* [ADR-002: Frontend Continuity & Presentation Layer Strategy (Jinja2 Port of Legacy JSPs)](#adr-002-frontend-continuity--presentation-layer-strategy-jinja2-port-of-legacy-jsps)
* [ADR-003: Persistence & ORM Framework (SQLAlchemy 2.0 with Data Mapper & Unit of Work)](#adr-003-persistence--orm-framework-sqlalchemy-20-with-data-mapper--unit-of-work)
* [ADR-004: Dual-Scalability & Stateless Session Architecture](#adr-004-dual-scalability--stateless-session-architecture)
* [ADR-005: Selective In-Memory Data Caching Strategy](#adr-005-selective-in-memory-data-caching-strategy)
* [ADR-006: Authentication & Security Modernization (Salted scrypt Hashing)](#adr-006-authentication--security-modernization-salted-scrypt-hashing)
* [ADR-007: Embedded AI-Native Capabilities (Semantic Search, Agent Tools, Pet Advisor)](#adr-007-embedded-ai-native-capabilities-semantic-search-agent-tools-pet-advisor)
* [ADR-008: Relational Database Strategy (SQLite for Demo / PostgreSQL for Production)](#adr-008-relational-database-strategy-sqlite-for-demo--postgresql-for-production)
* [ADR-009: Centralized Access Control & Session Hardening](#adr-009-centralized-access-control--session-hardening)

---

## ADR-001: Target Web Framework Selection (FastAPI + Uvicorn ASGI)

### Status
**Accepted**

### Context
Legacy JPetStore 6 runs on Java 11/17 inside a Tomcat Servlet container using Spring MVC 5.3 (app/WEB-INF/spring-mvc.xml). We need a modern Python web framework that supports high-throughput asynchronous execution, dual-mode serving (server-rendered HTML templates for UI continuity alongside auto-documented REST APIs for AI agents), and production maintainability.

### Options Considered
1. **Django:** Highly mature "batteries-included" framework, but heavily opinionated, synchronous by default, tightly coupled ORM, and excessive boilerplate overhead for an e-commerce API.
2. **Flask:** Lightweight and historically popular, but synchronous by default (WSGI), lacks native type-validation contracts, and requires numerous third-party plugins for OpenAPI documentation and async I/O.
3. **FastAPI (ASGI):** Modern asynchronous framework built on Starlette and Pydantic.

### Decision
Adopt **FastAPI** running on the **Uvicorn** ASGI web server.

### Consequences & Trade-offs
* **Positive:**
  * **Concurrency:** Asynchronous event loops let a single worker serve many concurrent I/O-bound requests (throughput was not load tested).
  * **Dual-Mode Capability:** Seamlessly serves Jinja2-rendered HTML pages for the user-facing web store while simultaneously exposing interactive OpenAPI 3.1 / Swagger endpoints at `/docs`.
  * **AI-Native Tool Integration:** Native Pydantic integration produces typed JSON schemas directly consumable by LLM agent tool-calling frameworks.
* **Negative:**
  * Requires strict adherence to asynchronous programming conventions (`async/await`) across route handlers.

---

## ADR-002: Frontend Continuity & Presentation Layer Strategy (Jinja2 Port of Legacy JSPs)

### Status
**Accepted**

### Context
The legacy UI consists of JSP 2.3 templates using JSTL tags (app/WEB-INF/jsp/), 38 static GIF assets (app/static/images/), and custom styling (app/static/css/jpetstore.css). The assessment requires retaining intended business behavior and demonstrating a functional application live.

### Options Considered
1. **Full Frontend Rewrite as a Single Page App (React / Vue / Next.js):** Decouples frontend and backend, but introduces massive token consumption, complex client-side state synchronization for checkout, and high risk of visual regressions.
2. **Jinja2 Server-Side Template Port:** Port legacy JSPs directly into Python Jinja2 templates, maintaining the exact HTML DOM hierarchy, CSS classes, and image references.

### Decision
Adopt **Option 2: Direct Jinja2 Template Port**.

### Consequences & Trade-offs
* **Positive:**
  * **Visual and Workflow Parity:** Reuses the original markup structure, CSS classes and images, preserving familiar JPetStore branding. Layout differences found during review are recorded in the issue log.
  * **Tokenomics Efficiency:** Avoids generating and validating a separate SPA front end, which reduces AI-assisted effort and test surface (not separately measured).
  * **1:1 Syntax Mapping:** JSTL tags (`<c:forEach>`, `<c:if>`, `<c:choose>`) map directly to Jinja2 syntax (`{% for %}`, `{% if %}`, `{% else %}`).
  * Reuses all 38 existing GIF assets and `jpetstore.css` directly.
* **Negative:**
  * Retains traditional server-rendered page reloads rather than an asynchronous SPA feel (though mitigatable via lightweight progressive enhancement if needed).

---

## ADR-003: Persistence & ORM Framework (SQLAlchemy 2.0 with Data Mapper & Unit of Work)

### Status
**Accepted**

### Context
Legacy JPetStore uses MyBatis 3 XML mappers (src/main/resources/org/mybatis/jpetstore/mapper/) which decouples SQL queries from domain POJOs. We need a mature, battle-tested Python persistence layer that maintains strict 3-tier architecture (`Repository` layer) and handles transactional integrity during order placement.

### Options Considered
1. **SQLModel:** Blends SQLAlchemy 2.0 with Pydantic v2 into unified classes. Great for rapid prototyping, but complex queries and advanced transactional row-locking defer to raw SQLAlchemy underneath.
2. **Tortoise ORM / Peewee:** Active Record ORMs (models save themselves via `item.save()`). Violates strict 3-tier separation of concerns and lacks advanced enterprise migration tooling.
3. **SQLAlchemy 2.0 + Alembic:** A mature, widely adopted Python ORM, based on Martin Fowler’s **Data Mapper** and **Unit of Work** design patterns.

### Decision
Adopt **SQLAlchemy 2.0** with **Alembic** for schema migrations and persistence.

### Consequences & Trade-offs
* **Positive:**
  * **Strict 3-Tier Architecture:** Data models remain pure Python entities; SQL logic is strictly encapsulated inside repository classes (`CatalogRepository`, `AccountRepository`, `OrderRepository`).
  * **Transaction Safety:** Native `AsyncSession` and Unit of Work pattern ensure atomic operations across orders, line items, and inventory decrementing (`OrderService`).
  * **Connection Pooling:** Built-in `QueuePool` prevents database connection starvation.
  * Modern Python type hinting (`Mapped[T]`, `mapped_column`) verified under `mypy --strict`.
* **Negative:**
  * Requires explicit repository classes rather than simple Active Record magic methods.

---

## ADR-004: Dual-Scalability & Stateless Session Architecture

### Status
**Accepted**

### Context
In legacy JPetStore, user sessions (cart items, account login state, checkout progress) are held in the JVM's `HttpSession`. If multiple Tomcat instances are deployed behind a load balancer, sessions break unless complex sticky-session routing or multicast session clustering is configured.

### Options Considered
1. **Server-Side Session Clustering (Redis):** Solves horizontal scaling, but requires running a dedicated Redis daemon, complicating local single-command demonstration.
2. **Stateless Cryptographically Signed Session Cookies:** Session data is serialized and signed using `itsdangerous` / Starlette `SessionMiddleware` and held in an HTTP-only client cookie. Signing makes the cookie tamper-evident but not encrypted, so only non-sensitive identifiers and cart references are stored.

### Decision
Adopt **Stateless Signed Session Cookies** with a pluggable repository abstraction ready for Redis clustering.

### Consequences & Trade-offs
* **Positive:**
  * **Horizontal Scale-Out:** The web tier holds no server-side session state, so any instance can serve any request behind a round-robin load balancer. Per-process catalog caches expire independently (see ADR-005).
  * **Zero Operational Overhead:** Requires zero external daemons (Redis/Memcached) for local development or assessment demonstration.
  * **Concurrency:** FastAPI's non-blocking event loops improve I/O concurrency per worker.
* **Negative:**
  * Cookie payload size limit (~4KB). Since JPetStore carts contain small SKU references and counts, typical cart payloads remain well under 1KB.
  * A signed cookie cannot be revoked server-side. To limit this, every authenticated request re-verifies the account against the database and clears stale sessions (see ADR-009).

---

## ADR-005: Selective In-Memory Data Caching Strategy

### Status
**Accepted**

### Context
An e-commerce platform exhibits high read-to-write asymmetry: most incoming traffic is read-only browsing (categories, products, item details). However, inventory counts and order sequences require strict transactional consistency.

### Decision
Implement a **Selective Cache-Aside Pattern** at the Repository/Service layer:
1. **Cached Data:** Static catalog data (`category`, `bannerdata`, `product`, `item` metadata) is cached in-process using bounded LRU caches with a 1-hour TTL. Search results use a query-level cache (`SearchCache`, TTL 3600 s, 256 entries).
2. **Excluded Data (NEVER Cached):**
   * `inventory.qty`: Queried in real-time to prevent overselling race conditions.
   * `sequence.nextid`: Atomic SQL sequence increment to guarantee unique order IDs.
   * `orders` & `lineitem`: Write-heavy, query-indexed by `userid`.

### Consequences & Trade-offs
* **Positive:**
  * Repeated reads of static catalog data avoid database round trips (latency not formally benchmarked).
  * Reduces repetitive catalog queries without external infrastructure (hit rate not measured).
  * Inventory reads are never served from cache, so stock checks during checkout are not stale.
* **Negative:**
  * In-process memory caches across multiple worker nodes expire independently on TTL (acceptable for static catalog data).

---

## ADR-006: Authentication & Security Modernization (Salted scrypt Hashing)

### Status
**Accepted** (amended: originally Argon2id, replaced by standard-library scrypt; see Issue 02 in the migration issue log)

### Context
The legacy application stores user passwords in table `signon` as **plaintext strings** (e.g. `'j2ee'`, `'ACID'`). This is a critical security weakness under modern standards. The client confirmed that fixing identified vulnerabilities is at the candidate's discretion.

### Options Considered
1. **Legacy Plaintext:** Retain plaintext for backward compatibility. (Rejected as unacceptable.)
2. **SHA-256 / MD5:** Fast, unsalted-by-default digests that are unsuitable for password storage.
3. **Argon2id (`argon2-cffi`):** Recommended modern algorithm. Initially selected, but `argon2-cffi` needs a native build that failed in the target Windows / Python environment (Issue 02).
4. **scrypt (`hashlib.scrypt`):** Memory-hard key derivation in the Python standard library. Recommended by OWASP as an alternative, with no native build dependency.

### Decision
Adopt **salted scrypt** via the standard library. Legacy demo credentials (`j2ee`, `ACID`) are seeded as in the legacy data load and are **upgraded to salted hashes on first successful login**; all new registrations are hashed at creation.

### Consequences & Trade-offs
* **Positive:**
  * Removes plaintext password storage from the live system once users sign in.
  * No native build dependency, so the application installs cleanly on any supported platform.
  * Evaluators can sign in immediately with the default credentials (`j2ee` / `j2ee`, `ACID` / `ACID`).
* **Negative:**
  * Until a seeded account signs in for the first time, its seed value is still plaintext in the database.
  * Argon2id is generally preferred where a native build is available; the hashing function is isolated in `account_service.py`, so switching later is a contained change.
  * Hashing costs CPU and memory per authentication, by design.

---

## ADR-007: Embedded AI-Native Capabilities (Semantic Search, Agent Tools, Pet Advisor)

### Status
**Accepted**

### Context
The assessment brief refers to AI-native modernization and evaluates AI-assisted engineering. The client confirmed that the approach is at the candidate's discretion, including adding AI capabilities such as a chatbot. A pure Java-to-Python rewrite would meet the functional goal, so a small set of AI capabilities was added to show how the system can be extended, with strict limits on cost and risk.

### Decision
Add three capabilities to the architecture:
1. **Natural Language Semantic Search:** In-process weighted scoring over product names, descriptions and category concepts. It finds results for conversational queries (e.g., *"quiet companion for apartment"*) that SQL `LIKE %keyword%` misses. No embedding model or vector store is used.
2. **Agent Tool-Calling Suite (`/api/v1/tools`):** Deterministic Pydantic v2 schemas and OpenAPI 3.1 endpoints that external LLM agents can discover and call.
3. **Cart-Aware Pet Advisor:** A rule-based recommendation engine that uses the active cart and profile preferences (`favcategory`) to suggest items, drawing only from real catalog entries.

None of these features calls an external LLM.

### Consequences & Trade-offs
* **Positive:**
  * No per-request token cost, no external service dependency, and catalog data stays in-process.
  * Deterministic and testable with standard `pytest` suites.
  * Demonstrable live in the UI and in the OpenAPI documentation.
* **Negative:**
  * Matching is keyword and concept based, so unusual phrasing may match less well than a learned model.
  * The scorer is isolated behind a service interface so an embedding-based or LLM-backed implementation can replace it later, at the cost of tokens, latency and an external dependency.

---

## ADR-008: Relational Database Strategy (SQLite for Demo / PostgreSQL for Production)

### Status
**Accepted**

### Context
Legacy JPetStore relies on an embedded in-memory HSQLDB database initialized on startup via src/main/resources/database/jpetstore-hsqldb-schema.sql and src/main/resources/database/jpetstore-hsqldb-dataload.sql.

### Options Considered
1. **HSQLDB via Java Bridge:** Fragile and defeats Python modernization.
2. **PostgreSQL Only:** High production fidelity, but requires evaluators to run an external PostgreSQL server or Docker container before testing.
3. **Dual Database Architecture (SQLite default + PostgreSQL production-ready via SQLAlchemy):** SQLite for zero-dependency local execution/evaluation; PostgreSQL for containerized multi-node production deployment.

### Decision
Adopt **Dual Database Strategy**: Default to **SQLite** (using Python's built-in driver) for zero-dependency local runs and automated tests, while configuring SQLAlchemy database URLs so **PostgreSQL** can be used in Docker by changing the database URL and installing an async PostgreSQL driver. The automated tests run against SQLite.

### Consequences & Trade-offs
* **Positive:**
  * Zero setup friction: Evaluator can run the application immediately with zero database installation.
  * Database schemas and seed data load identically.
  * A path to PostgreSQL via standard SQLAlchemy connection strings (the automated tests exercise SQLite).
* **Negative:**
  * SQL DDL scripts must remain standard ANSI SQL compatible with both SQLite and PostgreSQL.

---

## ADR-009: Centralized Access Control & Session Hardening

### Status
**Accepted**

### Context
Legacy controllers checked `session.getAttribute("accountBean")` individually inside action methods. Ad-hoc checks are easy to omit when a route is added. With signed client-side cookies there is an extra risk: a cookie stays valid after the account it names is deleted or locked. A review during development also found protected endpoints (checkout, profile update) relying on `request.session.get("username")` checks.

### Options Considered
1. **Per-route checks (legacy style):** Simple, but repeats code and risks omissions.
2. **Middleware that guards URL prefixes:** Central, but coarse and hard to combine with per-user data checks.
3. **A declarative FastAPI dependency (`get_current_active_user`):** Each protected route declares it, and the dependency verifies the account against the database.

### Decision
Adopt option 3 (`app/dependencies/auth.py`). Protected routes declare `current_user: Account = Depends(get_current_active_user)`. The dependency confirms the account still exists and is active, and clears the session if not. On sign-in the existing session is cleared before the identity is bound (anonymous cart state is preserved) to prevent session fixation. Unauthenticated web requests receive an HTTP 303 redirect to the sign-in form, and unauthenticated API requests receive HTTP 401 with a JSON error.

### Consequences & Trade-offs
* **Positive:**
  * Access control is declared in one place and visible in each route's signature.
  * Deleted or deactivated accounts lose access on the next request.
  * Web and API clients get appropriate responses for the same condition.
* **Negative:**
  * One database lookup per authenticated request.
  * The dependency must be applied to each new protected route, so route-level tests for unauthenticated access remain necessary.
