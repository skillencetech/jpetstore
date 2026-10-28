from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.repositories.account_repository import AccountRepository
from app.repositories.catalog_repository import CatalogRepository
from app.services.account_service import AccountService
from app.services.catalog_service import CatalogService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

LANGUAGES = ["english", "japanese"]
CATEGORIES = ["FISH", "DOGS", "REPTILES", "CATS", "BIRDS"]

@router.get("/account/signonForm", response_class=HTMLResponse)
async def signon_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account/signon.html",
        context={"user": request.session.get("user")}
    )

@router.post("/account/signon")
async def signon(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    service = AccountService(AccountRepository(db))
    account = await service.authenticate(username, password)
    if not account:
        return templates.TemplateResponse(
            request=request,
            name="account/signon.html",
            context={"error": "Invalid username or password.", "username": username}
        )
    request.session["user"] = await service.populate_user_session(account)
    return RedirectResponse(url="/catalog", status_code=303)

@router.get("/account/signoff")
async def signoff(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/catalog", status_code=303)

@router.get("/account/newAccountForm", response_class=HTMLResponse)
async def new_account_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="account/new_account.html",
        context={"languages": LANGUAGES, "categories": CATEGORIES, "user": request.session.get("user")}
    )

@router.post("/account/newAccount")
async def new_account(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    repeatedPassword: str = Form(...),
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address1: str = Form(...),
    address2: str = Form(""),
    city: str = Form(...),
    state: str = Form(...),
    zip: str = Form(...),
    country: str = Form(...),
    languagePreference: str = Form("english"),
    favouriteCategoryId: str = Form("DOGS"),
    listOption: bool = Form(False),
    bannerOption: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    if password != repeatedPassword:
        return templates.TemplateResponse(
            request=request,
            name="account/new_account.html",
            context={
                "error": "Passwords do not match.",
                "languages": LANGUAGES,
                "categories": CATEGORIES,
                "username": username
            }
        )

    service = AccountService(AccountRepository(db))
    existing = await service.get_account(username)
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="account/new_account.html",
            context={
                "error": "Username already exists.",
                "languages": LANGUAGES,
                "categories": CATEGORIES,
                "username": username
            }
        )

    account_info = {
        "firstName": firstName, "lastName": lastName, "email": email, "phone": phone,
        "address1": address1, "address2": address2, "city": city, "state": state,
        "zip": zip, "country": country
    }
    profile_info = {
        "languagePreference": languagePreference,
        "favouriteCategoryId": favouriteCategoryId,
        "listOption": listOption,
        "bannerOption": bannerOption
    }
    account = await service.register_account(username, password, account_info, profile_info)
    await db.commit()

    request.session["user"] = await service.populate_user_session(account)
    return RedirectResponse(url="/catalog", status_code=303)

@router.get("/account/editAccountForm", response_class=HTMLResponse)
@router.get("/account/profile", response_class=HTMLResponse)
async def edit_account_form(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/account/signonForm", status_code=303)

    service = AccountService(AccountRepository(db))
    account = await service.get_account(user["userid"])

    return templates.TemplateResponse(
        request=request,
        name="account/edit_account.html",
        context={
            "account": account,
            "languages": LANGUAGES,
            "categories": CATEGORIES,
            "user": user
        }
    )

@router.post("/account/editAccount")
async def edit_account(
    request: Request,
    password: Optional[str] = Form(None),
    repeatedPassword: Optional[str] = Form(None),
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address1: str = Form(...),
    address2: str = Form(""),
    city: str = Form(...),
    state: str = Form(...),
    zip: str = Form(...),
    country: str = Form(...),
    languagePreference: str = Form("english"),
    favouriteCategoryId: str = Form("DOGS"),
    listOption: bool = Form(False),
    bannerOption: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/account/signonForm", status_code=303)

    if password and password != repeatedPassword:
        service = AccountService(AccountRepository(db))
        account = await service.get_account(user["userid"])
        return templates.TemplateResponse(
            request=request,
            name="account/edit_account.html",
            context={
                "account": account,
                "languages": LANGUAGES,
                "categories": CATEGORIES,
                "error": "Passwords do not match.",
                "user": user
            }
        )

    service = AccountService(AccountRepository(db))
    account_info = {
        "firstName": firstName, "lastName": lastName, "email": email, "phone": phone,
        "address1": address1, "address2": address2, "city": city, "state": state,
        "zip": zip, "country": country
    }
    profile_info = {
        "languagePreference": languagePreference,
        "favouriteCategoryId": favouriteCategoryId,
        "listOption": listOption,
        "bannerOption": bannerOption
    }
    account = await service.update_account_profile(user["userid"], password, account_info, profile_info)
    await db.commit()

    account_with_profile = await service.get_account(user["userid"])
    request.session["user"] = await service.populate_user_session(account_with_profile or account)

    return RedirectResponse(url="/catalog", status_code=303)
