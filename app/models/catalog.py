from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Supplier(Base):
    __tablename__ = "supplier"

    suppid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(2), nullable=False)
    addr1: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    addr2: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    zip: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    items: Mapped[List["Item"]] = relationship("Item", back_populates="supplier_rel")

class Category(Base):
    __tablename__ = "category"

    catid: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    descn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category_rel")

class Product(Base):
    __tablename__ = "product"

    productid: Mapped[str] = mapped_column(String(10), primary_key=True)
    category: Mapped[str] = mapped_column(String(10), ForeignKey("category.catid"), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    descn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    category_rel: Mapped["Category"] = relationship("Category", back_populates="products")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="product_rel")

    @property
    def product_id(self) -> str:
        return self.productid

class Item(Base):
    __tablename__ = "item"

    itemid: Mapped[str] = mapped_column(String(10), primary_key=True)
    productid: Mapped[str] = mapped_column(String(10), ForeignKey("product.productid"), nullable=False)
    listprice: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    unitcost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    supplier: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("supplier.suppid"), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    attr1: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    attr2: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    attr3: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    attr4: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    attr5: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    product_rel: Mapped["Product"] = relationship("Product", back_populates="items", lazy="selectin")
    supplier_rel: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="items")
    inventory: Mapped[Optional["Inventory"]] = relationship("Inventory", back_populates="item_rel", uselist=False, lazy="selectin")

class Inventory(Base):
    __tablename__ = "inventory"

    itemid: Mapped[str] = mapped_column(String(10), ForeignKey("item.itemid"), primary_key=True)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)

    item_rel: Mapped["Item"] = relationship("Item", back_populates="inventory")
