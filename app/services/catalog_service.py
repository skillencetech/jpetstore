from app.models.catalog import Category, Item, Product
from app.repositories.catalog_repository import CatalogRepository


class CatalogService:
    def __init__(self, catalog_repo: CatalogRepository):
        self.repo = catalog_repo

    async def get_category_list(self) -> list[Category]:
        return await self.repo.get_category_list()

    async def get_category(self, catid: str) -> Category | None:
        return await self.repo.get_category(catid)

    async def get_product_list_by_category(self, catid: str) -> list[Product]:
        return await self.repo.get_product_list_by_category(catid)

    async def get_product(self, productid: str) -> Product | None:
        return await self.repo.get_product(productid)

    async def search_product_list(self, keywords: str) -> list[Product]:
        return await self.repo.search_product_list(keywords)

    async def get_item_list_by_product(self, productid: str) -> list[Item]:
        return await self.repo.get_item_list_by_product(productid)

    async def get_item(self, itemid: str) -> Item | None:
        return await self.repo.get_item(itemid)

    async def is_item_in_stock(self, itemid: str) -> bool:
        return await self.repo.is_item_in_stock(itemid)
