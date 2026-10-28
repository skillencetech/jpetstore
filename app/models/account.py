from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Signon(Base):
    __tablename__ = "signon"

    username: Mapped[str] = mapped_column(String(25), primary_key=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

class Account(Base):
    __tablename__ = "account"

    userid: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[str] = mapped_column(String(80), nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    addr1: Mapped[str] = mapped_column(String(80), nullable=False)
    addr2: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    zip: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(80), nullable=False)

    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="account", uselist=False, lazy="selectin")

class Profile(Base):
    __tablename__ = "profile"

    userid: Mapped[str] = mapped_column(String(80), ForeignKey("account.userid"), primary_key=True)
    langpref: Mapped[str] = mapped_column(String(80), nullable=False)
    favcategory: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    mylistopt: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    banneropt: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    account: Mapped["Account"] = relationship("Account", back_populates="profile", lazy="selectin")

class BannerData(Base):
    __tablename__ = "bannerdata"

    favcategory: Mapped[str] = mapped_column(String(80), primary_key=True)
    bannername: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
