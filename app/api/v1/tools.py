from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.catalog_repository import CatalogRepository
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/v1/tools", tags=["AI Agent Tools"])

class ProductToolResponse(BaseModel):
    product_id: str = Field(..., description="Unique product ID, e.g. FI-SW-01")
    category: str = Field(..., description="Pet Category")
    name: str = Field(..., description="Product Name")
    description: Optional[str] = Field(None, description="Detailed product description")

class ItemToolResponse(BaseModel):
    item_id: str = Field(..., description="SKU identifier, e.g. EST-1")
    product_id: str = Field(...)
    list_price: float = Field(...)
    attribute: Optional[str] = Field(None, description="Item variant attribute")
    in_stock: bool = Field(..., description="Real-time stock availability")

@router.get("/search_catalog", response_model=List[ProductToolResponse], summary="Search catalog items for AI agents")
async def search_catalog(keywords: str, db: AsyncSession = Depends(get_db)):
    """Search products using keyword queries with strict Pydantic schemas."""
    service = CatalogService(CatalogRepository(db))
    products = await service.search_product_list(keywords)
    return [
        ProductToolResponse(
            product_id=p.productid,
            category=p.category,
            name=p.name or "",
            description=p.descn
        )
        for p in products
    ]

@router.get("/get_item_details", response_model=ItemToolResponse, summary="Get SKU details and live stock")
async def get_item_details(item_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed SKU specification and inventory status."""
    service = CatalogService(CatalogRepository(db))
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    in_stock = await service.is_item_in_stock(item_id)
    return ItemToolResponse(
        item_id=item.itemid,
        product_id=item.productid,
        list_price=float(item.listprice or 0.0),
        attribute=item.attr1,
        in_stock=in_stock
    )
