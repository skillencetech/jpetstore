from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from app.config import get_settings
from app.database import init_db
from app.web.catalog_router import router as catalog_router
from app.web.cart_router import router as cart_router
from app.web.account_router import router as account_router
from app.web.order_router import router as order_router
from app.api.v1.tools import router as tools_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=settings.app_name,
    description="Modernized AI-Native JPetStore 6 (FastAPI, SQLAlchemy 2.0, Jinja2)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
    max_age=86400 * 7
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/jpetstore", StaticFiles(directory=static_dir), name="legacy_static")

# Web routers
app.include_router(catalog_router)
app.include_router(cart_router)
app.include_router(account_router)
app.include_router(order_router)

# AI-Native API routers
app.include_router(tools_router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "UP", "app": settings.app_name, "version": "1.0.0"}
