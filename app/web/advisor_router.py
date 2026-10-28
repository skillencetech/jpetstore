from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.catalog_repository import CatalogRepository
from app.services.catalog_service import CatalogService
from app.services.cart_service import CartService
from app.services.ai_service import AIService

router = APIRouter(prefix="/advisor", tags=["Pet Advisor Web"])

class ChatRequest(BaseModel):
    message: Optional[str] = ""

from typing import Optional

@router.get("/cart_insights")
async def get_cart_insights(
    request: Request,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    user = request.session.get("user")
    user_favcategory = user.get("favcategory") if user and isinstance(user, dict) else None

    # If user explicitly requested exploring a category (e.g. CATS, BIRDS)
    if category:
        selected_category = category.upper()
        insights = AIService.get_cart_advisor_insights([selected_category])
        insights["selected_category"] = selected_category
        insights["preferred_category"] = user_favcategory
        return insights

    # Check cart categories
    cart_data = CartService.get_cart_data(request.session)
    service = CatalogService(CatalogRepository(db))
    categories = []
    for item_id in cart_data.keys():
        item = await service.get_item(item_id)
        if item and item.product_rel:
            categories.append(item.product_rel.category)

    # If cart is empty, prioritize logged-in user's preferred category
    if not categories and user_favcategory:
        categories = [user_favcategory]

    insights = AIService.get_cart_advisor_insights(categories)
    insights["selected_category"] = categories[0] if categories else (user_favcategory or "DOGS")
    insights["preferred_category"] = user_favcategory
    return insights

@router.post("/chat")
async def advisor_chat(chat_req: ChatRequest):
    try:
        msg = chat_req.message or ""
        return AIService.answer_pet_question(msg)
    except Exception:
        return AIService.answer_pet_question("")
