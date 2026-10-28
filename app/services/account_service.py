import hashlib
import os
import secrets
from typing import Optional
from app.repositories.account_repository import AccountRepository
from app.models.account import Account, Profile, Signon, BannerData

class AccountService:
    def __init__(self, account_repo: AccountRepository):
        self.repo = account_repo

    def hash_password(self, password: str) -> str:
        """Hash password using memory-hard scrypt from Python standard library."""
        salt = secrets.token_hex(16)
        key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt.encode("utf-8"),
            n=16384,
            r=8,
            p=1
        )
        return f"scrypt:{salt}:{key.hex()}"

    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        """Verify plain password against stored hash with backward compatibility."""
        # 1. Plaintext compatibility for legacy jpetstore-6 dataset
        if stored_hash == plain_password:
            return True

        # 2. Scrypt hash verification
        if stored_hash.startswith("scrypt:"):
            try:
                _, salt, key_hex = stored_hash.split(":", 2)
                calc_key = hashlib.scrypt(
                    plain_password.encode("utf-8"),
                    salt=salt.encode("utf-8"),
                    n=16384,
                    r=8,
                    p=1
                )
                return secrets.compare_digest(calc_key.hex(), key_hex)
            except Exception:
                return False

        # 3. Fallback for Argon2 if present
        if stored_hash.startswith("$argon2"):
            try:
                from passlib.hash import argon2
                return argon2.verify(plain_password, stored_hash)
            except Exception:
                return False

        return False

    async def authenticate(self, username: str, password: str) -> Optional[Account]:
        signon = await self.repo.get_signon(username)
        if not signon:
            return None
        if not self.verify_password(password, signon.password):
            return None
        # Auto-upgrade plaintext to scrypt on successful login
        if signon.password == password and not signon.password.startswith("scrypt:"):
            signon.password = self.hash_password(password)
            await self.repo.update_signon(signon)
        return await self.repo.get_account(username)

    async def get_account(self, username: str) -> Optional[Account]:
        return await self.repo.get_account(username)

    async def get_banner_data(self, favcategory: str) -> Optional[BannerData]:
        return await self.repo.get_banner_data(favcategory)
