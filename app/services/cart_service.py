from decimal import Decimal
from typing import Any, cast

from app.models.catalog import Item


class CartItem:
    def __init__(self, item: Item, quantity: int = 1):
        self.item = item
        self.item_id = item.itemid
        self.product_id = item.productid
        self.description = f"{item.attr1 or ''} {item.product_rel.name if item.product_rel else ''}".strip()
        self.in_stock = (item.inventory.qty > 0) if item.inventory else True
        self.quantity = quantity
        self.list_price = Decimal(str(item.listprice or 0.00))

    @property
    def total(self) -> Decimal:
        return self.list_price * self.quantity


class CartService:
    @staticmethod
    def get_cart_data(session: dict[str, Any]) -> dict[str, int]:
        cart = session.get("cart")
        if isinstance(cart, dict):
            return cast(dict[str, int], cart)
        return {}

    @staticmethod
    def add_item(session: dict, item_id: str, quantity: int = 1):
        cart = session.get("cart", {})
        cart[item_id] = cart.get(item_id, 0) + quantity
        session["cart"] = cart

    @staticmethod
    def set_quantity(session: dict, item_id: str, quantity: int):
        cart = session.get("cart", {})
        if quantity <= 0:
            cart.pop(item_id, None)
        else:
            cart[item_id] = quantity
        session["cart"] = cart

    @staticmethod
    def remove_item(session: dict, item_id: str):
        cart = session.get("cart", {})
        cart.pop(item_id, None)
        session["cart"] = cart

    @staticmethod
    def clear_cart(session: dict):
        session["cart"] = {}

    @staticmethod
    def calculate_subtotal(cart_items: list[CartItem]) -> Decimal:
        return sum((item.total for item in cart_items), Decimal("0.00"))
