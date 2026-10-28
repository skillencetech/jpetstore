from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.account_repository import AccountRepository
from app.services.account_service import AccountService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/account/signonForm", response_class=HTMLResponse)
async def signon_form(request: Request):
    return templates.TemplateResponse("account/signon.html", {"request": request, "user": request.session.get("user")})

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
            "account/signon.html",
            {"request": request, "error": "Invalid username or password.", "username": username}
        )
    request.session["user"] = {
        "userid": account.userid,
        "firstname": account.firstname,
        "lastname": account.lastname,
        "email": account.email
    }
    return RedirectResponse(url="/catalog", status_code=303)

@router.get("/account/signoff")
async def signoff(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/catalog", status_code=303)
