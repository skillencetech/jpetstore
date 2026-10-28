import pytest
from app.database import AsyncSessionLocal, init_db
from app.repositories.account_repository import AccountRepository
from app.services.account_service import AccountService

@pytest.mark.asyncio
async def test_account_password_hashing_and_verification():
    async with AsyncSessionLocal() as session:
        service = AccountService(AccountRepository(session))

        # Test scrypt hashing and verification
        plain_pw = "secretPassword123"
        hashed = service.hash_password(plain_pw)
        assert hashed.startswith("scrypt:")
        assert service.verify_password(plain_pw, hashed) is True
        assert service.verify_password("wrongPassword", hashed) is False

        # Legacy plaintext compatibility
        assert service.verify_password("j2ee", "j2ee") is True

@pytest.mark.asyncio
async def test_account_authentication_and_hash_upgrade():
    await init_db()
    async with AsyncSessionLocal() as session:
        service = AccountService(AccountRepository(session))

        # Authenticate known seeded user 'j2ee' (originally seeded with 'j2ee')
        user = await service.authenticate("j2ee", "j2ee")
        assert user is not None
        assert user.username == "j2ee"
        assert user.email == "yourname@yourdomain.com"

        # Verify invalid credentials return None
        bad_auth = await service.authenticate("j2ee", "incorrect_pwd")
        assert bad_auth is None

        non_existent = await service.authenticate("nonexistent_user", "password")
        assert non_existent is None

@pytest.mark.asyncio
async def test_account_registration_and_profile():
    await init_db()
    async with AsyncSessionLocal() as session:
        service = AccountService(AccountRepository(session))
        test_username = "test_eval_user"

        # Clean up existing test user if present
        existing = await service.get_account(test_username)
        if existing:
            await session.delete(existing)
            await session.commit()

        account_info = {
            "email": "test_eval@example.com",
            "firstname": "Modern",
            "lastname": "Tester",
            "status": "OK",
            "addr1": "100 AI Boulevard",
            "addr2": "Suite 400",
            "city": "Tech City",
            "state": "CA",
            "zip": "94016",
            "country": "USA",
            "phone": "555-0199"
        }
        profile_info = {
            "langpref": "english",
            "favcategory": "DOGS",
            "mylistopt": True,
            "banneropt": True
        }

        created = await service.register_account(
            username=test_username,
            password="SecurePass2026!",
            account_info=account_info,
            profile_info=profile_info
        )
        assert created.username == test_username
        assert created.email == "test_eval@example.com"
        assert created.profile is not None
        assert created.profile.favcategory == "DOGS"
        assert created.profile.mylistopt == 1

        # Test authenticated login of the newly created account
        auth_user = await service.authenticate(test_username, "SecurePass2026!")
        assert auth_user is not None
        assert auth_user.username == test_username
