import numpy as np
from rapidocr_onnxruntime import RapidOCR
from app.core.config import MODEL_PATH
from app.crud.ocr_record import create_record
from app.database import AsyncSessionLocal

class OCRService:
    def __init__(self):
        self.model = RapidOCR()

    async def process_bytes(self, data: bytes):
        """
        对输入字节流进行 OCR，返回文本、对应多边形坐标和置信度
        并将识别文本写入数据库
        """
        res, _ = self.model(data)

        texts, polys, scores = [], [], []
        for item in res:
            box, text, score = item
            polys.append(np.array(box))
            texts.append(text)
            scores.append(score)

        # 写入数据库
        db = AsyncSessionLocal()
        create_record(db, filename="bytes_input", text="\n".join(texts))
        db.close()

        # 返回 OCR 全部信息
        return {
            "texts": texts,
            "polys": polys,
            "scores": scores
        }

    async def process_path(self, path: str):
        res, _ = self.model(path)
        return {"texts": [r[1] for r in res]}

ocr_service = OCRService()