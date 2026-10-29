from datetime import date
from decimal import Decimal

from app.models.order import LineItem, Order, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartItem


class OutOfStockException(Exception):
    pass


class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.repo = order_repo

    async def create_order(
        self,
        userid: str,
        cart_items: list[CartItem],
        bill_info: dict,
        ship_info: dict,
        credit_card: str,
        expr_date: str,
        card_type: str,
        courier: str = "UPS",
        locale: str = "en_US",
    ) -> Order:
        if not cart_items:
            raise ValueError("Cart is empty")

        for ci in cart_items:
            ok = await self.repo.decrement_inventory(ci.item_id, ci.quantity)
            if not ok:
                raise OutOfStockException(f"Item {ci.item_id} has insufficient stock")

        order_id = await self.repo.get_next_order_id()
        total_price = sum((ci.total for ci in cart_items), Decimal("0.00"))

        order = Order(
            orderid=order_id,
            userid=userid,
            orderdate=date.today(),
            shipaddr1=ship_info.get("addr1", ""),
            shipaddr2=ship_info.get("addr2", ""),
            shipcity=ship_info.get("city", ""),
            shipstate=ship_info.get("state", ""),
            shipzip=ship_info.get("zip", ""),
            shipcountry=ship_info.get("country", ""),
            billaddr1=bill_info.get("addr1", ""),
            billaddr2=bill_info.get("addr2", ""),
            billcity=bill_info.get("city", ""),
            billstate=bill_info.get("state", ""),
            billzip=bill_info.get("zip", ""),
            billcountry=bill_info.get("country", ""),
            courier=courier,
            totalprice=total_price,
            billtofirstname=bill_info.get("firstname", ""),
            billtolastname=bill_info.get("lastname", ""),
            shiptofirstname=ship_info.get("firstname", ""),
            shiptolastname=ship_info.get("lastname", ""),
            creditcard=credit_card,
            exprdate=expr_date,
            cardtype=card_type,
            locale=locale,
        )
        await self.repo.insert_order(order)

        for idx, ci in enumerate(cart_items, start=1):
            line_item = LineItem(
                orderid=order_id, linenum=idx, itemid=ci.item_id, quantity=ci.quantity, unitprice=ci.list_price
            )
            await self.repo.insert_line_item(line_item)

        status = OrderStatus(orderid=order_id, linenum=1, timestamp=date.today(), status="P")
        await self.repo.insert_order_status(status)

        return order

    async def get_order(self, orderid: int) -> Order | None:
        return await self.repo.get_order(orderid)

    async def get_orders_by_username(self, username: str) -> list[Order]:
        return await self.repo.get_orders_by_username(username)
