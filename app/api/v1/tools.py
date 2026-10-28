from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.catalog_repository import CatalogRepository
from app.services.catalog_service import CatalogService
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/v1/tools", tags=["AI Agent Tools (OpenAPI 3.1)"])

class ProductToolResponse(BaseModel):
    product_id: str = Field(..., description="Unique product identifier (e.g., FI-SW-01, K9-BD-01)")
    category: str = Field(..., description="Pet Category: FISH, DOGS, REPTILES, CATS, BIRDS")
    name: str = Field(..., description="Display name of the pet or product")
    description: Optional[str] = Field(None, description="Detailed attributes and habitat specifications")

class ItemToolResponse(BaseModel):
    item_id: str = Field(..., description="SKU identifier, e.g. EST-1")
    product_id: str = Field(..., description="Associated parent product ID")
    list_price: float = Field(..., description="Unit retail price in USD")
    attribute: Optional[str] = Field(None, description="Variant specification (e.g. Male Adult, Small)")
    in_stock: bool = Field(..., description="True if available in inventory")
    inventory_quantity: int = Field(..., description="Available inventory count")

class QuoteItemInput(BaseModel):
    item_id: str = Field(..., description="SKU to purchase, e.g. EST-1")
    quantity: int = Field(1, ge=1, description="Quantity to purchase")

class QuoteItemOutput(BaseModel):
    item_id: str
    product_name: str
    unit_price: float
    quantity: int
    line_total: float

class OrderQuoteResponse(BaseModel):
    items: List[QuoteItemOutput]
    subtotal: float
    estimated_tax: float
    shipping_cost: float
    grand_total: float

class AdvisorRecommendationInput(BaseModel):
    cart_category_ids: List[str] = Field(default=[], description="List of category names currently in cart")

class AdvisorRecommendationResponse(BaseModel):
    categories_analyzed: List[str]
    care_advice: List[str]
    recommended_accessories: List[dict]

@router.get("/search_catalog", response_model=List[ProductToolResponse], summary="Natural Language & Semantic Catalog Search")
async def search_catalog(
    keywords: str = Query(..., description="Search query or conversational intent, e.g. 'friendly dog for kids' or 'Koi'"),
    semantic: bool = Query(True, description="Enable semantic AI matching over raw SQL keyword matching"),
    db: AsyncSession = Depends(get_db)
):
    """Allows autonomous AI agents to search store inventory using natural language intents."""
    service = CatalogService(CatalogRepository(db))
    if semantic:
        categories = await service.get_category_list()
        full_catalog = []
        for cat in categories:
            prods = await service.get_product_list_by_category(cat.catid)
            full_catalog.extend(prods)
        matched = AIService.semantic_product_search(keywords, full_catalog)
    else:
        matched = await service.search_product_list(keywords)

    return [
        ProductToolResponse(
            product_id=p.productid,
            category=p.category,
            name=p.name or "",
            description=p.descn
        )
        for p in matched
    ]

@router.get("/item/{item_id}", response_model=ItemToolResponse, summary="Retrieve SKU Specs & Live Inventory")
@router.get("/get_item_details", response_model=ItemToolResponse, summary="Retrieve SKU Specs & Live Inventory (Query Param)")
async def get_item_details(
    item_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve detailed unit price, variant traits, and real-time stock balance."""
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id is required")
    repo = CatalogRepository(db)
    service = CatalogService(repo)
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"SKU '{item_id}' not found")
    in_stock = await service.is_item_in_stock(item_id)
    qty = await repo.get_inventory_quantity(item_id)
    return ItemToolResponse(
        item_id=item.itemid,
        product_id=item.productid,
        list_price=float(item.listprice or 0.0),
        attribute=item.attr1,
        in_stock=in_stock,
        inventory_quantity=qty
    )

@router.get("/check_stock/{item_id}", summary="Check Real-Time Stock Balance")
async def check_stock(item_id: str, db: AsyncSession = Depends(get_db)):
    """Check inventory stock for a SKU."""
    repo = CatalogRepository(db)
    service = CatalogService(repo)
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"SKU '{item_id}' not found")
    in_stock = await service.is_item_in_stock(item_id)
    qty = await repo.get_inventory_quantity(item_id)
    return {"item_id": item_id, "in_stock": in_stock, "quantity": qty}


@router.post("/calculate_order_quote", response_model=OrderQuoteResponse, summary="Agent Pre-Purchase Price Quote")
async def calculate_order_quote(
    quote_req: List[QuoteItemInput],
    db: AsyncSession = Depends(get_db)
):
    """Calculates order totals, applicable 7% sales tax, and standard flat shipping quote."""
    if not quote_req:
        raise HTTPException(status_code=400, detail="Quote request cannot be empty")

    service = CatalogService(CatalogRepository(db))
    items_out = []
    subtotal = Decimal("0.00")

    for req in quote_req:
        item = await service.get_item(req.item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"SKU {req.item_id} does not exist")
        unit_price = item.listprice or Decimal("0.00")
        line_total = unit_price * req.quantity
        subtotal += line_total
        p_name = item.product_rel.name if item.product_rel else req.item_id
        items_out.append(QuoteItemOutput(
            item_id=item.itemid,
            product_name=f"{item.attr1 or ''} {p_name}".strip(),
            unit_price=float(unit_price),
            quantity=req.quantity,
            line_total=float(line_total)
        ))

    tax = subtotal * Decimal("0.07")
    shipping = Decimal("10.00")
    grand_total = subtotal + tax + shipping

    return OrderQuoteResponse(
        items=items_out,
        subtotal=float(subtotal),
        estimated_tax=float(round(tax, 2)),
        shipping_cost=float(shipping),
        grand_total=float(round(grand_total, 2))
    )

@router.post("/advisor_recommendations", response_model=AdvisorRecommendationResponse, summary="AI Pet Care & Accessory Advisor (Recommendation Endpoint)")
@router.post("/pet_advisor", response_model=AdvisorRecommendationResponse, summary="AI Pet Care & Accessory Advisor")
async def get_pet_advisor(req: AdvisorRecommendationInput):

    """Returns tailored pet care protocols and complementary accessory recommendations."""
    insights = AIService.get_cart_advisor_insights(req.cart_category_ids)
    return AdvisorRecommendationResponse(
        categories_analyzed=insights["categories"],
        care_advice=insights["advice"],
        recommended_accessories=insights["recommended_accessories"]
    )
