import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from app.services.cart_service import CartService, CartItem
from app.models.catalog import Item, Product, Inventory

def create_mock_item(item_id: str, product_id: str, list_price: float, qty: int = 10, attr1: str = "Adult Male") -> Item:
    item = Item(
        itemid=item_id,
        productid=product_id,
        listprice=Decimal(str(list_price)),
        unitcost=Decimal("10.00"),
        supplier=1,
        status="P",
        attr1=attr1
    )
    product = Product(productid=product_id, category="FISH", name="Angelfish", descn="Saltwater fish")
    inv = Inventory(itemid=item_id, qty=qty)
    item.product_rel = product
    item.inventory = inv
    return item

def test_cart_item_properties():
    item = create_mock_item("EST-1", "FI-SW-01", 16.50, qty=5, attr1="Large")
    cart_item = CartItem(item=item, quantity=2)

    assert cart_item.item_id == "EST-1"
    assert cart_item.product_id == "FI-SW-01"
    assert cart_item.quantity == 2
    assert cart_item.list_price == Decimal("16.50")
    assert cart_item.total == Decimal("33.00")
    assert cart_item.in_stock is True
    assert "Large" in cart_item.description

def test_cart_service_stateless_session_flow():
    session = {}

    # 1. Add item
    CartService.add_item(session, "EST-1", quantity=1)
    assert session["cart"] == {"EST-1": 1}

    # 2. Add more of the same item
    CartService.add_item(session, "EST-1", quantity=2)
    assert session["cart"] == {"EST-1": 3}

    # 3. Add second item
    CartService.add_item(session, "EST-2", quantity=1)
    assert session["cart"] == {"EST-1": 3, "EST-2": 1}

    # 4. Update quantity
    CartService.set_quantity(session, "EST-1", quantity=5)
    assert session["cart"]["EST-1"] == 5

    # 5. Setting quantity <= 0 removes item
    CartService.set_quantity(session, "EST-2", quantity=0)
    assert "EST-2" not in session["cart"]

    # 6. Explicit remove item
    CartService.remove_item(session, "EST-1")
    assert session["cart"] == {}

    # 7. Clear cart
    CartService.add_item(session, "EST-3", quantity=2)
    CartService.clear_cart(session)
    assert session["cart"] == {}

def test_cart_subtotal_calculation():
    item1 = create_mock_item("EST-1", "FI-SW-01", 10.50)
    item2 = create_mock_item("EST-2", "FI-SW-02", 5.25)

    cart_items = [
        CartItem(item=item1, quantity=2), # 21.00
        CartItem(item=item2, quantity=4)  # 21.00
    ]

    subtotal = CartService.calculate_subtotal(cart_items)
    assert subtotal == Decimal("42.00")
