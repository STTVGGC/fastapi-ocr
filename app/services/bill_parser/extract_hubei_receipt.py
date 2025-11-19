# services/bill_parser/extract_hubei_receipt.py

from .utils import merge_right_value, find_key_value
from .amount_converter import chinese_to_num


def extract_hubei_receipt(texts, polys, scores):
    """
    电建集团 · 湖北工程公司 · 进账凭证字段提取器
    """

    bill_data = {}

    # 1. 抽取“交易流水号”
    key_text = "交易流水号："
    for idx, text in enumerate(texts):
        if key_text in text.strip():
            value = merge_right_value(idx, texts, polys, scores, key_text)
            if value and value['text']:
                bill_data['transaction_no'] = value['text']
            break  # 找到第一个匹配即可

    # 2. 锚点“收款人”提取右边账号
    anchor_text = "收款人"
    key_list = ["账号"]
    res = find_key_value(anchor_text, key_list, texts, polys, scores)
    if res.get("账号") and res["账号"]["text"]:
        bill_data['payee_account'] = res["账号"]["text"]

    # 3. 锚点“付款人”提取多个字段
    anchor_text = "付款人"
    key_list = ["单位名称", "账号", "开户银行"]
    res = find_key_value(anchor_text, key_list, texts, polys, scores)
    if res.get("单位名称") and res["单位名称"]["text"]:
        bill_data['payer'] = res["单位名称"]["text"]
    if res.get("账号") and res["账号"]["text"]:
        bill_data['payer_account'] = res["账号"]["text"]
    if res.get("开户银行") and res["开户银行"]["text"]:
        bill_data['payer_bank'] = res["开户银行"]["text"]

    # 4. 提取“大写金额”，并转为数字
    for key_text in ["金额 (大写)", "金额(大写)"]:
        for idx, text in enumerate(texts):
            if key_text in text.strip():
                value = merge_right_value(idx, texts, polys, scores, key_text, max_x_gap=60)
                if value and value['text']:
                    bill_data['amount_upper'] = value['text']
                    bill_data['amount'] = chinese_to_num(value['text'])
                break

    # 5. 提取“用途”
    key_text = "用途"
    for idx, text in enumerate(texts):
        if key_text in text.strip():
            value = merge_right_value(idx, texts, polys, scores, key_text)
            if value and value['text']:
                bill_data['purpose'] = value['text']
            break

    return bill_data
