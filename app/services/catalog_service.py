from typing import List, Optional
from app.repositories.catalog_repository import CatalogRepository
from app.models.catalog import Category, Product, Item

class CatalogService:
    def __init__(self, catalog_repo: CatalogRepository):
        self.repo = catalog_repo

    async def get_category_list(self) -> List[Category]:
        return await self.repo.get_category_list()

    async def get_category(self, catid: str) -> Optional[Category]:
        return await self.repo.get_category(catid)

    async def get_product_list_by_category(self, catid: str) -> List[Product]:
        return await self.repo.get_product_list_by_category(catid)

    async def get_product(self, productid: str) -> Optional[Product]:
        return await self.repo.get_product(productid)

    async def search_product_list(self, keywords: str) -> List[Product]:
        return await self.repo.search_product_list(keywords)

    async def get_item_list_by_product(self, productid: str) -> List[Item]:
        return await self.repo.get_item_list_by_product(productid)

    async def get_item(self, itemid: str) -> Optional[Item]:
        return await self.repo.get_item(itemid)

    async def is_item_in_stock(self, itemid: str) -> bool:
        return await self.repo.is_item_in_stock(itemid)
