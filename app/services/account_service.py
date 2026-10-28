from typing import Optional
from passlib.hash import argon2
from app.repositories.account_repository import AccountRepository
from app.models.account import Account, Profile, Signon, BannerData

class AccountService:
    def __init__(self, account_repo: AccountRepository):
        self.repo = account_repo

    def hash_password(self, password: str) -> str:
        return argon2.hash(password)

    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        if stored_hash == plain_password:
            return True
        try:
            return argon2.verify(plain_password, stored_hash)
        except Exception:
            return False

    async def authenticate(self, username: str, password: str) -> Optional[Account]:
        signon = await self.repo.get_signon(username)
        if not signon:
            return None
        if not self.verify_password(password, signon.password):
            return None
        # Auto-upgrade plaintext to Argon2id on successful login per ADR-006
        if signon.password == password and not signon.password.startswith("$argon2"):
            signon.password = self.hash_password(password)
            await self.repo.update_signon(signon)
        return await self.repo.get_account(username)

    async def get_account(self, username: str) -> Optional[Account]:
        return await self.repo.get_account(username)

    async def get_banner_data(self, favcategory: str) -> Optional[BannerData]:
        return await self.repo.get_banner_data(favcategory)
