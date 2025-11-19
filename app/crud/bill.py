# app/crud/bill.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.bill import Bill
from sqlalchemy.ext.asyncio import AsyncSession

# 创建票据记录（写入数据库）
async def create_bill(db: AsyncSession, bill_data: dict):
    bill = Bill(**bill_data)       # 将 dict 转换为 Bill 对象
    db.add(bill)                   # 添加到数据库会话
    await db.commit()                    # 提交事务（真正写入数据库）
    await db.refresh(bill)               # 刷新对象，获得数据库生成的 ID
    return bill

# 插入或更新票据记录（根据 transaction_no 唯一标识）
async def upsert_bill(db: AsyncSession, data: dict):
    # 先查是否存在
    # existing = await db.query(Bill).filter(Bill.transaction_no == data["transaction_no"]).first()

    result = await db.execute(
        select(Bill).where(Bill.transaction_no == data["transaction_no"])
    )
    existing = result.scalars().first()

    if existing:
        # 更新字段
        for key, value in data.items():
            setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return existing  # 返回更新后的记录
    else:
        # 创建新记录
        new_bill = Bill(**data)
        db.add(new_bill)
        await db.commit()
        await db.refresh(new_bill)
        return new_bill



# 查询单条票据
async def get_bill(db: AsyncSession, bill_id: int):
    # return db.query(Bill).filter(Bill.id == bill_id).first()
    result = await db.execute(
        select(Bill).where(Bill.id == bill_id)
    )
    return result.scalars().first()

# 查询多条票据（带分页）
async def get_bills(db: AsyncSession, skip: int = 0, limit: int = 100):
    # return db.query(Bill).offset(skip).limit(limit).all()
    result = await db.execute(
        select(Bill).offset(skip).limit(limit)
    )
    return result.scalars().all()

# 更新票据信息
async def update_bill(db: AsyncSession, bill_id: int, updates: dict):
    bill = await get_bill(db, bill_id)
    if not bill:
        return None

    # 将 updates 中的每个字段写入 bill 对象
    for key, value in updates.items():
        setattr(bill, key, value)

    await db.commit()                    # 提交
    await db.refresh(bill)               # 刷新
    return bill


# 删除票据
async def delete_bill(db: AsyncSession, bill_id: int):
    bill =await get_bill(db, bill_id)
    if not bill:
        return None

    await db.delete(bill)
    await db.commit()
    return bill
