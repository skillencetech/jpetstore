from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.account_repository import AccountRepository
from app.services.catalog_service import CatalogService
from app.services.account_service import AccountService
from app.services.cart_service import CartService, CartItem

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/cart", response_class=HTMLResponse)
async def view_cart(request: Request, db: AsyncSession = Depends(get_db)):
    cart_data = CartService.get_cart_data(request.session)
    service = CatalogService(CatalogRepository(db))
    cart_items = []
    for item_id, qty in cart_data.items():
        item = await service.get_item(item_id)
        if item:
            cart_items.append(CartItem(item, qty))
    subtotal = CartService.calculate_subtotal(cart_items)

    user = request.session.get("user")
    my_list = []
    if user:
        account_service = AccountService(AccountRepository(db))
        if "banner_name" not in user or "mylistopt" not in user:
            account = await account_service.get_account(user["userid"])
            if account:
                user = await account_service.populate_user_session(account)
                request.session["user"] = user

        if user.get("mylistopt") and user.get("favcategory"):
            my_list = await service.get_product_list_by_category(user["favcategory"])

    return templates.TemplateResponse(
        request=request,
        name="cart/cart.html",
        context={
            "cart_items": cart_items,
            "subtotal": subtotal,
            "user": user,
            "my_list": my_list
        }
    )

@router.post("/cart/items/{item_id}")
async def add_to_cart(request: Request, item_id: str):
    CartService.add_item(request.session, item_id, 1)
    return RedirectResponse(url="/cart", status_code=303)

@router.post("/cart/update")
async def update_cart(request: Request):
    form = await request.form()
    for key, val in form.items():
        if key.startswith("qty_"):
            item_id = key.replace("qty_", "")
            try:
                qty = int(val)
                CartService.set_quantity(request.session, item_id, qty)
            except ValueError:
                pass
    return RedirectResponse(url="/cart", status_code=303)

@router.get("/cart/items/{item_id}/remove")
async def remove_from_cart(request: Request, item_id: str):
    CartService.remove_item(request.session, item_id)
    return RedirectResponse(url="/cart", status_code=303)
