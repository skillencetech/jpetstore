import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.mark.asyncio
async def test_tools_search_catalog():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Standard keyword query
        response = await client.get("/api/v1/tools/search_catalog?keywords=fish&semantic=false")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any("FI-" in item["product_id"] for item in data)

        # 2. Semantic query
        response_sem = await client.get("/api/v1/tools/search_catalog?keywords=friendly+dog+companion&semantic=true")
        assert response_sem.status_code == 200
        data_sem = response_sem.json()
        assert isinstance(data_sem, list)
        assert len(data_sem) > 0

@pytest.mark.asyncio
async def test_tools_item_details_and_stock():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Check existing item
        res = await client.get("/api/v1/tools/item/EST-1")
        assert res.status_code == 200
        data = res.json()
        assert data["item_id"] == "EST-1"
        assert data["product_id"] == "FI-SW-01"
        assert "list_price" in data
        assert "inventory_quantity" in data

        # Check stock endpoint
        res_stock = await client.get("/api/v1/tools/check_stock/EST-1")
        assert res_stock.status_code == 200
        stock_data = res_stock.json()
        assert stock_data["item_id"] == "EST-1"
        assert "in_stock" in stock_data
        assert "quantity" in stock_data

        # Non-existent item
        res_404 = await client.get("/api/v1/tools/item/NONEXISTENT-999")
        assert res_404.status_code == 404

@pytest.mark.asyncio
async def test_tools_calculate_order_quote():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        quote_payload = [
            {"item_id": "EST-1", "quantity": 2},
            {"item_id": "EST-2", "quantity": 1}
        ]
        res = await client.post("/api/v1/tools/calculate_order_quote", json=quote_payload)
        assert res.status_code == 200
        data = res.json()
        assert "subtotal" in data
        assert "estimated_tax" in data
        assert "shipping_cost" in data
        assert "grand_total" in data
        assert len(data["items"]) == 2
        assert data["grand_total"] == round(data["subtotal"] + data["estimated_tax"] + data["shipping_cost"], 2)

@pytest.mark.asyncio
async def test_tools_advisor_recommendations():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {"cart_category_ids": ["FISH", "BIRDS"]}
        res = await client.post("/api/v1/tools/advisor_recommendations", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "care_advice" in data
        assert "recommended_accessories" in data
        assert len(data["care_advice"]) > 0
