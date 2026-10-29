import pytest

from app.database import AsyncSessionLocal, init_db
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartItem
from app.services.catalog_service import CatalogService
from app.services.order_service import OrderService, OutOfStockException


@pytest.mark.asyncio
async def test_order_creation_and_inventory_decrement():
    await init_db()
    async with AsyncSessionLocal() as session:
        order_repo = OrderRepository(session)
        catalog_repo = CatalogRepository(session)
        order_service = OrderService(order_repo)
        catalog_service = CatalogService(catalog_repo)

        # Retrieve a valid item with inventory
        item = await catalog_service.get_item("EST-1")
        assert item is not None
        initial_stock = item.inventory.qty
        assert initial_stock >= 2

        cart_item = CartItem(item=item, quantity=2)
        bill_info = {
            "firstname": "John",
            "lastname": "Doe",
            "addr1": "123 Main St",
            "addr2": "Apt 4B",
            "city": "Boston",
            "state": "MA",
            "zip": "02101",
            "country": "USA",
        }
        ship_info = bill_info.copy()

        order = await order_service.create_order(
            userid="j2ee",
            cart_items=[cart_item],
            bill_info=bill_info,
            ship_info=ship_info,
            credit_card="9999999999999999",
            expr_date="12/28",
            card_type="Visa",
            courier="UPS",
        )

        assert order.orderid > 0
        assert order.userid == "j2ee"
        assert order.totalprice == cart_item.total

        # Re-fetch item to verify inventory was decremented
        updated_item = await catalog_service.get_item("EST-1")
        assert updated_item.inventory.qty == initial_stock - 2

        # Verify order retrieval by orderid
        fetched_order = await order_service.get_order(order.orderid)
        assert fetched_order is not None
        assert fetched_order.orderid == order.orderid
        assert len(fetched_order.line_items) == 1
        assert fetched_order.line_items[0].itemid == "EST-1"
        assert fetched_order.line_items[0].quantity == 2


@pytest.mark.asyncio
async def test_order_out_of_stock_exception():
    await init_db()
    async with AsyncSessionLocal() as session:
        order_repo = OrderRepository(session)
        catalog_repo = CatalogRepository(session)
        order_service = OrderService(order_repo)
        catalog_service = CatalogService(catalog_repo)

        item = await catalog_service.get_item("EST-2")
        assert item is not None
        excessive_qty = item.inventory.qty + 1000

        cart_item = CartItem(item=item, quantity=excessive_qty)
        bill_info = {"firstname": "Jane", "lastname": "Doe"}

        with pytest.raises(OutOfStockException):
            await order_service.create_order(
                userid="j2ee",
                cart_items=[cart_item],
                bill_info=bill_info,
                ship_info=bill_info,
                credit_card="1111222233334444",
                expr_date="01/29",
                card_type="MasterCard",
            )
