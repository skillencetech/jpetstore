from datetime import date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Sequence(Base):
    __tablename__ = "sequence"

    name: Mapped[str] = mapped_column(String(30), primary_key=True)
    nextid: Mapped[int] = mapped_column(Integer, nullable=False)

class Order(Base):
    __tablename__ = "orders"

    orderid: Mapped[int] = mapped_column(Integer, primary_key=True)
    userid: Mapped[str] = mapped_column(String(80), ForeignKey("account.userid"), nullable=False)
    orderdate: Mapped[date] = mapped_column(Date, nullable=False)
    shipaddr1: Mapped[str] = mapped_column(String(80), nullable=False)
    shipaddr2: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    shipcity: Mapped[str] = mapped_column(String(80), nullable=False)
    shipstate: Mapped[str] = mapped_column(String(80), nullable=False)
    shipzip: Mapped[str] = mapped_column(String(20), nullable=False)
    shipcountry: Mapped[str] = mapped_column(String(20), nullable=False)
    billaddr1: Mapped[str] = mapped_column(String(80), nullable=False)
    billaddr2: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    billcity: Mapped[str] = mapped_column(String(80), nullable=False)
    billstate: Mapped[str] = mapped_column(String(80), nullable=False)
    billzip: Mapped[str] = mapped_column(String(20), nullable=False)
    billcountry: Mapped[str] = mapped_column(String(20), nullable=False)
    courier: Mapped[str] = mapped_column(String(80), nullable=False)
    totalprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    billtofirstname: Mapped[str] = mapped_column(String(80), nullable=False)
    billtolastname: Mapped[str] = mapped_column(String(80), nullable=False)
    shiptofirstname: Mapped[str] = mapped_column(String(80), nullable=False)
    shiptolastname: Mapped[str] = mapped_column(String(80), nullable=False)
    creditcard: Mapped[str] = mapped_column(String(80), nullable=False)
    exprdate: Mapped[str] = mapped_column(String(7), nullable=False)
    cardtype: Mapped[str] = mapped_column(String(80), nullable=False)
    locale: Mapped[str] = mapped_column(String(80), nullable=False)

    line_items: Mapped[List["LineItem"]] = relationship("LineItem", back_populates="order_rel")
    statuses: Mapped[List["OrderStatus"]] = relationship("OrderStatus", back_populates="order_rel")

class OrderStatus(Base):
    __tablename__ = "orderstatus"

    orderid: Mapped[int] = mapped_column(Integer, ForeignKey("orders.orderid"), primary_key=True)
    linenum: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(2), nullable=False)

    order_rel: Mapped["Order"] = relationship("Order", back_populates="statuses")

class LineItem(Base):
    __tablename__ = "lineitem"

    orderid: Mapped[int] = mapped_column(Integer, ForeignKey("orders.orderid"), primary_key=True)
    linenum: Mapped[int] = mapped_column(Integer, primary_key=True)
    itemid: Mapped[str] = mapped_column(String(10), ForeignKey("item.itemid"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unitprice: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order_rel: Mapped["Order"] = relationship("Order", back_populates="line_items")
