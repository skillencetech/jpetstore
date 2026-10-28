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
    message: str

@router.get("/cart_insights")
async def get_cart_insights(request: Request, db: AsyncSession = Depends(get_db)):
    cart_data = CartService.get_cart_data(request.session)
    service = CatalogService(CatalogRepository(db))
    categories = []
    for item_id in cart_data.keys():
        item = await service.get_item(item_id)
        if item and item.product_rel:
            categories.append(item.product_rel.category)
    return AIService.get_cart_advisor_insights(categories)

@router.post("/chat")
async def advisor_chat(chat_req: ChatRequest):
    return AIService.answer_pet_question(chat_req.message)
