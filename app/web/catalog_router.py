from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.database import get_db
from app.repositories.catalog_repository import CatalogRepository
from app.services.catalog_service import CatalogService
from app.services.ai_service import AIService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/catalog")

@router.get("/catalog", response_class=HTMLResponse)
async def catalog_main(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="catalog/main.html",
        context={"user": request.session.get("user")}
    )

@router.get("/catalog/categories/{category_id}", response_class=HTMLResponse)
async def view_category(request: Request, category_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(CatalogRepository(db))
    category = await service.get_category(category_id)
    product_list = await service.get_product_list_by_category(category_id)
    return templates.TemplateResponse(
        request=request,
        name="catalog/category.html",
        context={"category": category, "product_list": product_list, "user": request.session.get("user")}
    )

@router.get("/catalog/products/{product_id}", response_class=HTMLResponse)
async def view_product(request: Request, product_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(CatalogRepository(db))
    product = await service.get_product(product_id)
    item_list = await service.get_item_list_by_product(product_id)
    return templates.TemplateResponse(
        request=request,
        name="catalog/product.html",
        context={"product": product, "item_list": item_list, "user": request.session.get("user")}
    )

@router.get("/catalog/items/{item_id}", response_class=HTMLResponse)
async def view_item(request: Request, item_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(CatalogRepository(db))
    item = await service.get_item(item_id)
    in_stock = await service.is_item_in_stock(item_id)
    return templates.TemplateResponse(
        request=request,
        name="catalog/item.html",
        context={"item": item, "in_stock": in_stock, "user": request.session.get("user")}
    )

@router.get("/catalog/search", response_class=HTMLResponse)
async def search(request: Request, keywords: str = "", db: AsyncSession = Depends(get_db)):
    service = CatalogService(CatalogRepository(db))
    product_list = await service.search_product_list(keywords)
    is_semantic = False

    if not product_list and keywords.strip():
        categories = await service.get_category_list()
        all_prods = []
        for cat in categories:
            prods = await service.get_product_list_by_category(cat.catid)
            all_prods.extend(prods)
        product_list = AIService.semantic_product_search(keywords, all_prods)
        is_semantic = True

    return templates.TemplateResponse(
        request=request,
        name="catalog/search.html",
        context={
            "product_list": product_list,
            "keywords": keywords,
            "is_semantic": is_semantic,
            "user": request.session.get("user")
        }
    )
