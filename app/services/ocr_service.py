from rapidocr_onnxruntime import RapidOCR
from core.config import MODEL_PATH

class OCRService:
    def __init__(self):
        # self.model = RapidOCR(det_model_path=MODEL_PATH)
        self.model = RapidOCR()
    async def process_bytes(self, data: bytes):
        res, _ = self.model(data)
        return {"texts": [r[1] for r in res]}

    async def process_path(self, path: str):
        res, _ = self.model(path)
        return {"texts": [r[1] for r in res]}

ocr_service = OCRService()

