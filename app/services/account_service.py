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
        if stored_hash == plain_password:
            return True
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
        if signon.password == password and not signon.password.startswith("scrypt:"):
            signon.password = self.hash_password(password)
            await self.repo.update_signon(signon)
        return await self.repo.get_account(username)

    async def register_account(self, username: str, password: str, account_info: dict, profile_info: dict) -> Account:
        hashed_pw = self.hash_password(password)
        signon = Signon(username=username, password=hashed_pw)
        account = Account(
            userid=username,
            email=account_info.get("email", ""),
            firstname=account_info.get("firstName", ""),
            lastname=account_info.get("lastName", ""),
            status="OK",
            addr1=account_info.get("address1", ""),
            addr2=account_info.get("address2", ""),
            city=account_info.get("city", ""),
            state=account_info.get("state", ""),
            zip=account_info.get("zip", ""),
            country=account_info.get("country", ""),
            phone=account_info.get("phone", "")
        )
        profile = Profile(
            userid=username,
            langpref=profile_info.get("languagePreference", "english"),
            favcategory=profile_info.get("favouriteCategoryId", "DOGS"),
            mylistopt=1 if profile_info.get("listOption") else 0,
            banneropt=1 if profile_info.get("bannerOption") else 0
        )
        await self.repo.insert_account(account, profile, signon)
        return account

    async def update_account_profile(self, username: str, password: Optional[str], account_info: dict, profile_info: dict) -> Account:
        account = await self.repo.get_account(username)
        if not account:
            raise ValueError("Account not found")
        account.email = account_info.get("email", account.email)
        account.firstname = account_info.get("firstName", account.firstname)
        account.lastname = account_info.get("lastName", account.lastname)
        account.addr1 = account_info.get("address1", account.addr1)
        account.addr2 = account_info.get("address2", account.addr2)
        account.city = account_info.get("city", account.city)
        account.state = account_info.get("state", account.state)
        account.zip = account_info.get("zip", account.zip)
        account.country = account_info.get("country", account.country)
        account.phone = account_info.get("phone", account.phone)
        await self.repo.update_account(account)

        if account.profile:
            account.profile.langpref = profile_info.get("languagePreference", account.profile.langpref)
            account.profile.favcategory = profile_info.get("favouriteCategoryId", account.profile.favcategory)
            account.profile.mylistopt = 1 if profile_info.get("listOption") else 0
            account.profile.banneropt = 1 if profile_info.get("bannerOption") else 0
            await self.repo.update_profile(account.profile)

        if password and password.strip():
            signon = await self.repo.get_signon(username)
            if signon:
                signon.password = self.hash_password(password)
                await self.repo.update_signon(signon)

        return account

    async def get_account(self, username: str) -> Optional[Account]:
        return await self.repo.get_account(username)

    async def get_banner_data(self, favcategory: str) -> Optional[BannerData]:
        return await self.repo.get_banner_data(favcategory)

    async def populate_user_session(self, account: Account) -> dict:
        banner_name = ""
        favcategory = None
        banneropt = 0
        mylistopt = 0
        if account.profile:
            favcategory = account.profile.favcategory
            banneropt = account.profile.banneropt or 0
            mylistopt = account.profile.mylistopt or 0
            if favcategory:
                banner_data = await self.get_banner_data(favcategory)
                if banner_data and banner_data.bannername:
                    banner_name = banner_data.bannername.replace("<image ", "<img ").replace("<image>", "<img>")
        return {
            "userid": account.userid,
            "firstname": account.firstname,
            "lastname": account.lastname,
            "email": account.email,
            "favcategory": favcategory,
            "banneropt": banneropt,
            "mylistopt": mylistopt,
            "banner_name": banner_name
        }
