import pytest
from app.database import AsyncSessionLocal, init_db
from app.repositories.catalog_repository import CatalogRepository
from app.services.catalog_service import CatalogService

@pytest.mark.asyncio
async def test_catalog_service():
    await init_db()
    async with AsyncSessionLocal() as session:
        service = CatalogService(CatalogRepository(session))
        categories = await service.get_category_list()
        assert len(categories) == 5

        products = await service.get_product_list_by_category("FISH")
        assert len(products) > 0

        item = await service.get_item("EST-1")
        assert item is not None
        assert item.productid == "FI-SW-01"
