from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import Account
from app.repositories.account_repository import AccountRepository


class NotAuthenticatedException(Exception):
    """Raised when an unauthenticated client requests a protected web resource."""

    pass


async def get_current_user_optional(request: Request, db: AsyncSession = Depends(get_db)) -> Account | None:
    """
    Inspects the cryptographic HMAC session for user identity and verifies
    active account existence in the database. If the account is deactivated,
    deleted, or the session is tampered, the session is purged.
    """
    user_session = request.session.get("user")
    if not user_session or not isinstance(user_session, dict) or "userid" not in user_session:
        return None

    username = user_session["userid"]
    account_repo = AccountRepository(db)
    account = await account_repo.get_account(username)

    if not account:
        # Invalidate stale/ghost session
        request.session.pop("user", None)
        return None

    return account


async def get_current_active_user(
    request: Request, user: Account | None = Depends(get_current_user_optional)
) -> Account:
    """
    Declarative dependency requiring a valid, active authenticated user.
    Raises NotAuthenticatedException for web requests (triggering a 303 redirect to signon)
    or HTTP 401 Unauthorized for REST API requests.
    """
    if not user:
        if request.url.path.startswith("/api/"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please authenticate before invoking this tool.",
            )
        raise NotAuthenticatedException()

    return user
