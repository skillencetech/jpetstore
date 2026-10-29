from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.account import Account, BannerData, Profile, Signon
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository):
    async def get_account(self, username: str) -> Account | None:
        stmt = select(Account).where(Account.userid == username).options(selectinload(Account.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_signon(self, username: str) -> Signon | None:
        stmt = select(Signon).where(Signon.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert_account(self, account: Account, profile: Profile, signon: Signon):
        self.session.add(account)
        self.session.add(profile)
        self.session.add(signon)
        await self.session.flush()

    async def update_account(self, account: Account):
        await self.session.merge(account)
        await self.session.flush()

    async def update_profile(self, profile: Profile):
        await self.session.merge(profile)
        await self.session.flush()

    async def update_signon(self, signon: Signon):
        await self.session.merge(signon)
        await self.session.flush()

    async def get_banner_data(self, favcategory: str) -> BannerData | None:
        stmt = select(BannerData).where(BannerData.favcategory == favcategory)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
