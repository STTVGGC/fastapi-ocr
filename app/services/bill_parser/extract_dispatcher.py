# services/bill_parser/extract_dispatcher.py

from .extract_hubei_receipt import extract_hubei_receipt

def extract_fields(texts, polys, scores):
    """
    自动选择合适的解析器
    """
    # 按票据类型判断
    if any("中国电建集团财务有限责任公司进账凭证" in t for t in texts):
        return extract_hubei_receipt(texts, polys, scores)

    return {}  # 默认空
