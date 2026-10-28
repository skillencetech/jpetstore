from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.account_repository import AccountRepository
from app.services.catalog_service import CatalogService
from app.services.order_service import OrderService, OutOfStockException
from app.services.account_service import AccountService
from app.services.cart_service import CartService, CartItem

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

CREDIT_CARD_TYPES = ["Visa", "MasterCard", "American Express"]

@router.get("/order/newOrderForm", response_class=HTMLResponse)
async def new_order_form(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/account/signonForm", status_code=303)

    cart_data = CartService.get_cart_data(request.session)
    if not cart_data:
        return RedirectResponse(url="/cart", status_code=303)

    account_service = AccountService(AccountRepository(db))
    account = await account_service.get_account(user["userid"])

    return templates.TemplateResponse(
        request=request,
        name="order/new_order_form.html",
        context={
            "account": account,
            "creditCardTypes": CREDIT_CARD_TYPES,
            "user": user
        }
    )

@router.post("/order/new")
async def process_new_order(
    request: Request,
    cardType: str = Form(...),
    creditCard: str = Form(...),
    expiryDate: str = Form(...),
    billToFirstName: str = Form(...),
    billToLastName: str = Form(...),
    billAddress1: str = Form(...),
    billAddress2: str = Form(""),
    billCity: str = Form(...),
    billState: str = Form(...),
    billZip: str = Form(...),
    billCountry: str = Form(...),
    shippingAddressRequired: bool = Form(False)
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/account/signonForm", status_code=303)

    pending_order = {
        "cardType": cardType,
        "creditCard": creditCard,
        "expiryDate": expiryDate,
        "billToFirstName": billToFirstName,
        "billToLastName": billToLastName,
        "billAddress1": billAddress1,
        "billAddress2": billAddress2,
        "billCity": billCity,
        "billState": billState,
        "billZip": billZip,
        "billCountry": billCountry,
        # Default shipping address to billing address
        "shipToFirstName": billToFirstName,
        "shipToLastName": billToLastName,
        "shipAddress1": billAddress1,
        "shipAddress2": billAddress2,
        "shipCity": billCity,
        "shipState": billState,
        "shipZip": billZip,
        "shipCountry": billCountry,
        "courier": "UPS"
    }
    request.session["pending_order"] = pending_order

    if shippingAddressRequired:
        return RedirectResponse(url="/order/shippingForm", status_code=303)
    return RedirectResponse(url="/order/confirmOrder", status_code=303)

@router.get("/order/shippingForm", response_class=HTMLResponse)
async def shipping_form(request: Request):
    user = request.session.get("user")
    pending_order = request.session.get("pending_order")
    if not user or not pending_order:
        return RedirectResponse(url="/order/newOrderForm", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="order/shipping_form.html",
        context={"order": pending_order, "user": user}
    )

@router.post("/order/shipping")
async def process_shipping(
    request: Request,
    shipToFirstName: str = Form(...),
    shipToLastName: str = Form(...),
    shipAddress1: str = Form(...),
    shipAddress2: str = Form(""),
    shipCity: str = Form(...),
    shipState: str = Form(...),
    shipZip: str = Form(...),
    shipCountry: str = Form(...)
):
    pending_order = request.session.get("pending_order", {})
    pending_order["shipToFirstName"] = shipToFirstName
    pending_order["shipToLastName"] = shipToLastName
    pending_order["shipAddress1"] = shipAddress1
    pending_order["shipAddress2"] = shipAddress2
    pending_order["shipCity"] = shipCity
    pending_order["shipState"] = shipState
    pending_order["shipZip"] = shipZip
    pending_order["shipCountry"] = shipCountry
    request.session["pending_order"] = pending_order

    return RedirectResponse(url="/order/confirmOrder", status_code=303)

@router.get("/order/confirmOrder", response_class=HTMLResponse)
async def confirm_order(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    pending_order = request.session.get("pending_order")
    if not user or not pending_order:
        return RedirectResponse(url="/order/newOrderForm", status_code=303)

    cart_data = CartService.get_cart_data(request.session)
    catalog_service = CatalogService(CatalogRepository(db))
    cart_items = []
    for item_id, qty in cart_data.items():
        item = await catalog_service.get_item(item_id)
        if item:
            cart_items.append(CartItem(item, qty))
    subtotal = CartService.calculate_subtotal(cart_items)

    return templates.TemplateResponse(
        request=request,
        name="order/confirm_order.html",
        context={
            "order": pending_order,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "user": user
        }
    )

@router.post("/order/confirm")
async def submit_order(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    pending_order = request.session.get("pending_order")
    if not user or not pending_order:
        return RedirectResponse(url="/catalog", status_code=303)

    cart_data = CartService.get_cart_data(request.session)
    catalog_service = CatalogService(CatalogRepository(db))
    cart_items = []
    for item_id, qty in cart_data.items():
        item = await catalog_service.get_item(item_id)
        if item:
            cart_items.append(CartItem(item, qty))

    order_service = OrderService(OrderRepository(db))
    try:
        bill_info = {
            "firstname": pending_order["billToFirstName"],
            "lastname": pending_order["billToLastName"],
            "addr1": pending_order["billAddress1"],
            "addr2": pending_order["billAddress2"],
            "city": pending_order["billCity"],
            "state": pending_order["billState"],
            "zip": pending_order["billZip"],
            "country": pending_order["billCountry"],
        }
        ship_info = {
            "firstname": pending_order["shipToFirstName"],
            "lastname": pending_order["shipToLastName"],
            "addr1": pending_order["shipAddress1"],
            "addr2": pending_order["shipAddress2"],
            "city": pending_order["shipCity"],
            "state": pending_order["shipState"],
            "zip": pending_order["shipZip"],
            "country": pending_order["shipCountry"],
        }
        order = await order_service.create_order(
            userid=user["userid"],
            cart_items=cart_items,
            bill_info=bill_info,
            ship_info=ship_info,
            credit_card=pending_order["creditCard"],
            expr_date=pending_order["expiryDate"],
            card_type=pending_order["cardType"],
            courier=pending_order.get("courier", "UPS"),
            locale="en_US"
        )
        await db.commit()

        # Clear cart and pending session
        CartService.clear_cart(request.session)
        request.session.pop("pending_order", None)

        return RedirectResponse(url=f"/order/viewOrder/{order.orderid}", status_code=303)
    except OutOfStockException as e:
        await db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="order/confirm_order.html",
            context={
                "order": pending_order,
                "cart_items": cart_items,
                "subtotal": CartService.calculate_subtotal(cart_items),
                "error": str(e),
                "user": user
            }
        )

@router.get("/order/viewOrder/{order_id}", response_class=HTMLResponse)
async def view_order(request: Request, order_id: int, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    order_service = OrderService(OrderRepository(db))
    order = await order_service.get_order(order_id)
    if not order:
        return RedirectResponse(url="/catalog", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="order/view_order.html",
        context={"order": order, "user": user}
    )

@router.get("/order/list", response_class=HTMLResponse)
async def list_orders(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/account/signonForm", status_code=303)

    order_service = OrderService(OrderRepository(db))
    orders = await order_service.get_orders_by_username(user["userid"])

    return templates.TemplateResponse(
        request=request,
        name="order/list_orders.html",
        context={"orders": orders, "user": user}
    )
