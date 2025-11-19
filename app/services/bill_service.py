# services/bill_service.py

from app.database import AsyncSessionLocal
from app.crud.bill import create_bill, upsert_bill
from app.services.ocr_service import ocr_service
from text import extract_fields_from_ocr
from app.services.bill_parser.extract_dispatcher import extract_fields

# 票据服务层
# 职责：调用 OCR，然后写入数据库
class BillService:

    async def process_and_save(self, file_bytes: bytes):
        """
        处理流程：
        1）OCR 识别
        2）字段提取（你已有的 extract_fields()）
        3）写入数据库
        """

        # 执行 OCR
        ocr_result = await ocr_service.process_bytes(file_bytes)

        # 直接解构三个列表
        texts = ocr_result["texts"]
        polys = ocr_result["polys"]
        scores = ocr_result["scores"]

        # 将 OCR 文本解析成票据字段（你需要实现的函数）
        bill_data = extract_fields(texts, polys, scores)

        # 创建数据库会话
        db = AsyncSessionLocal()

        # 写入或更新票据信息
        bill =await upsert_bill(db, bill_data)

        # 关闭数据库连接
        db.close()

        return bill


bill_service = BillService()
