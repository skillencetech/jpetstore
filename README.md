# JPetStore 6 - AI-Native Modernized Platform

Modernized enterprise implementation of **MyBatis JPetStore 6**, migrated to an **AI-Native, Dual-Scalable Python Architecture** following [jpetstore_migration_proposal_and_roadmap.md](docs/jpetstore_migration_proposal_and_roadmap.md).

---

## 1. Architectural Highlights
- **Framework:** FastAPI running on Uvicorn (ASGI event-loop).
- **Presentation:** 100% visual parity using Jinja2 templates and original assets.
- **Persistence:** SQLAlchemy 2.0 async engine with connection pooling and 3-tier architecture.
- **Scalability:** Stateless signed cookie sessions (horizontal scale-out ready) and in-memory LRU data caching.
- **Security:** Argon2id password hashing with legacy plaintext auto-upgrading.
- **AI-Native:** OpenAPI 3.1 agent tool-calling endpoints at `/api/v1/tools`.

---

## 2. Quick Start

### Prerequisites
- Python 3.10+ (Recommended Python 3.12)
- Virtual Environment (`venv`)

### Setup & Run
```bash
# 1. Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Application
python run.py
```

The application starts at: **http://127.0.0.1:8080**
- Storefront: `http://127.0.0.1:8080/catalog`
- OpenAPI / Swagger Docs: `http://127.0.0.1:8080/docs`
- Health Check: `http://127.0.0.1:8080/health`

---

## 3. Project Directory Structure
```
jpetstore/
├── app/
│   ├── api/v1/tools.py          # AI Agent Tool Calling
│   ├── config.py                # Pydantic Settings
│   ├── database.py              # Async SQLAlchemy Engine & Session
│   ├── models/                  # Catalog, Account, Order Entities
│   ├── repositories/            # 3-Tier Persistence Layer with Caching
│   ├── services/                # Business Logic Services
│   ├── static/                  # 38 GIF Images & jpetstore.css
│   ├── templates/               # Jinja2 JSP Parity Templates
│   ├── web/                     # Web Routers (Catalog, Cart, Account)
│   └── main.py                  # ASGI Application
├── sql/
│   ├── schema.sql               # ANSI Relational DDL
│   └── dataload.sql             # JPetStore Seed Dataset
├── tests/                       # Automated Pytest Suite
├── requirements.txt             # Python Dependencies
├── run.py                       # Development Entrypoint
└── README.md
```
