from app.web.account_router import router as account_router
from app.web.cart_router import router as cart_router
from app.web.catalog_router import router as catalog_router
from app.web.order_router import router as order_router

__all__ = ["catalog_router", "cart_router", "account_router", "order_router"]
