# routers/bill.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.database import get_db
from app.services.bill_service import bill_service
from app.crud.bill import get_bill, get_bills, update_bill, delete_bill
from app.schemas import BillUpdate
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter(tags=["Bills"])

# 上传文件 → OCR → 自动入库
@router.post("/bills/ocr")
async def upload_and_ocr(file: UploadFile = File(...)):
    data = await file.read()
    bill = await bill_service.process_and_save(data)
    return bill


# 查询所有票据
@router.get("/bills")
async def list_bills(db: AsyncSession = Depends(get_db)):
    return await get_bills(db)


# 查询单条票据
@router.get("/bills/{bill_id}")
async def read_bill(bill_id: int, db: AsyncSession = Depends(get_db)):
    bill = await get_bill(db, bill_id)
    if not bill:
        raise HTTPException(404, "票据不存在")
    return bill


# 修改票据
@router.put("/bills/{bill_id}")
async def update_bill_api(bill_id: int, updates: BillUpdate, db: AsyncSession = Depends(get_db)):
    bill = await update_bill(db, bill_id, updates.dict(exclude_unset=True))#只更新提供的字段
    if not bill:
        raise HTTPException(404, "票据不存在")
    return bill


# 删除票据
@router.delete("/bills/{bill_id}")
async def delete_bill_api(bill_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_bill(db, bill_id)
    if not deleted:
        raise HTTPException(404, "票据不存在")
    return {"message": "票据已删除"}
