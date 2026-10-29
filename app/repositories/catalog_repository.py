import time
from collections import OrderedDict

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.models.catalog import Category, Inventory, Item, Product
from app.repositories.base import BaseRepository

# In-memory selective cache dictionary per ADR-005
_CATEGORY_CACHE: dict[str, Category] = {}
_CATEGORY_LIST_CACHE: list[Category] | None = None
_PRODUCT_CACHE: dict[str, Product] = {}
_PRODUCT_LIST_CACHE: dict[str, list[Product]] = {}
_ITEM_CACHE: dict[str, Item] = {}


class SearchCache:
    """High-performance LRU cache with TTL for search queries."""

    def __init__(self, maxsize: int = 256, ttl_seconds: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, list[Product]]] = OrderedDict()

    def get(self, query: str) -> list[Product] | None:
        key = query.strip().lower()
        if key in self._cache:
            created_at, results = self._cache[key]
            if time.time() - created_at < self.ttl:
                self._cache.move_to_end(key)
                return results
            else:
                del self._cache[key]
        return None

    def set(self, query: str, results: list[Product]):
        key = query.strip().lower()
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (time.time(), results)
        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)


_SEARCH_CACHE = SearchCache(maxsize=256, ttl_seconds=3600)


class CatalogRepository(BaseRepository):
    @staticmethod
    def get_search_cache() -> SearchCache:
        return _SEARCH_CACHE

    async def get_category_list(self) -> list[Category]:
        global _CATEGORY_LIST_CACHE
        if _CATEGORY_LIST_CACHE is not None:
            return _CATEGORY_LIST_CACHE
        stmt = select(Category).order_by(Category.catid)
        result = await self.session.execute(stmt)
        categories = list(result.scalars().all())
        _CATEGORY_LIST_CACHE = categories
        return categories

    async def get_category(self, catid: str) -> Category | None:
        if catid in _CATEGORY_CACHE:
            return _CATEGORY_CACHE[catid]
        stmt = select(Category).where(Category.catid == catid)
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()
        if category:
            _CATEGORY_CACHE[catid] = category
        return category

    async def get_product_list_by_category(self, catid: str) -> list[Product]:
        if catid in _PRODUCT_LIST_CACHE:
            return _PRODUCT_LIST_CACHE[catid]
        stmt = select(Product).where(Product.category == catid).order_by(Product.productid)
        result = await self.session.execute(stmt)
        products = list(result.scalars().all())
        _PRODUCT_LIST_CACHE[catid] = products
        return products

    async def get_product(self, productid: str) -> Product | None:
        if productid in _PRODUCT_CACHE:
            return _PRODUCT_CACHE[productid]
        stmt = select(Product).where(Product.productid == productid)
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()
        if product:
            _PRODUCT_CACHE[productid] = product
        return product

    async def search_product_list(self, keywords: str) -> list[Product]:
        cached = _SEARCH_CACHE.get(keywords)
        if cached is not None:
            return cached

        tokens = [k.strip().lower() for k in keywords.split() if k.strip()]
        if not tokens:
            return []
        stmt = select(Product)
        conditions = []
        for token in tokens:
            conditions.append(Product.name.ilike(f"%{token}%"))
            conditions.append(Product.category.ilike(f"%{token}%"))
            conditions.append(Product.descn.ilike(f"%{token}%"))
        stmt = stmt.where(or_(*conditions)).order_by(Product.name)
        result = await self.session.execute(stmt)
        products = list(result.scalars().all())
        _SEARCH_CACHE.set(keywords, products)
        return products

    async def get_item_list_by_product(self, productid: str) -> list[Item]:
        stmt = (
            select(Item)
            .where(Item.productid == productid)
            .options(selectinload(Item.product_rel), selectinload(Item.inventory))
            .order_by(Item.itemid)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_item(self, itemid: str) -> Item | None:
        stmt = (
            select(Item)
            .where(Item.itemid == itemid)
            .options(
                selectinload(Item.product_rel).selectinload(Product.category_rel),
                selectinload(Item.supplier_rel),
                selectinload(Item.inventory),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def is_item_in_stock(self, itemid: str) -> bool:
        stmt = select(Inventory.qty).where(Inventory.itemid == itemid)
        result = await self.session.execute(stmt)
        qty = result.scalar_one_or_none()
        return (qty is not None) and (qty > 0)

    async def get_inventory_quantity(self, itemid: str) -> int:
        stmt = select(Inventory.qty).where(Inventory.itemid == itemid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or 0
