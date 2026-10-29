from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.catalog import Inventory, Item
from app.models.order import LineItem, Order, OrderStatus, Sequence
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository):
    async def get_next_order_id(self) -> int:
        stmt = select(Sequence).where(Sequence.name == "ordernum")
        result = await self.session.execute(stmt)
        seq = result.scalar_one_or_none()
        if not seq:
            seq = Sequence(name="ordernum", nextid=1000)
            self.session.add(seq)
            await self.session.flush()
        next_id = seq.nextid
        seq.nextid = next_id + 1
        await self.session.flush()
        return next_id

    async def insert_order(self, order: Order):
        self.session.add(order)
        await self.session.flush()

    async def insert_order_status(self, order_status: OrderStatus):
        self.session.add(order_status)
        await self.session.flush()

    async def insert_line_item(self, line_item: LineItem):
        self.session.add(line_item)
        await self.session.flush()

    async def decrement_inventory(self, itemid: str, quantity: int) -> bool:
        stmt = select(Inventory).where(Inventory.itemid == itemid)
        result = await self.session.execute(stmt)
        inventory = result.scalar_one_or_none()
        if not inventory or inventory.qty < quantity:
            return False
        inventory.qty -= quantity
        await self.session.flush()
        return True

    async def get_order(self, orderid: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.orderid == orderid)
            .options(
                selectinload(Order.statuses),
                selectinload(Order.line_items).selectinload(LineItem.item_rel).selectinload(Item.product_rel),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_orders_by_username(self, username: str) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.userid == username)
            .options(
                selectinload(Order.statuses),
                selectinload(Order.line_items).selectinload(LineItem.item_rel).selectinload(Item.product_rel),
            )
            .order_by(Order.orderdate.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
