from rapidocr_onnxruntime import RapidOCR
import numpy as np

def correct_common_text_errors(text):
    corrections = {
        "项自经理部": "项目经理部",  # OCR常识别错误
        "，勿重复记账使用。": "",  # 清理无关信息
        "参": "叁",  # 误识别的中文数字
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text


def robust_merge_multiline_value(key_idx, texts, polys, scores, key_text, max_y_gap=10, max_x_gap=200):
    """
    用于拼接某个key右边多行的value（比如账号、银行信息）。
    只考虑key右边【X坐标近】【Y坐标重叠或相近】的内容。
    """

    key_box = polys[key_idx]  # key的四点坐标框
    key_xmax = np.max(key_box[:, 0])  # key的右边界x坐标
    key_ymin = np.min(key_box[:, 1])
    key_ymax = np.max(key_box[:, 1])

    # 找出右边候选内容框
    candidates = []
    for idx, text in enumerate(texts):
        if idx == key_idx or text.strip() == key_text:
            continue
        box = polys[idx]
        x_min = np.min(box[:, 0])
        y_min = np.min(box[:, 1])
        y_max = np.max(box[:, 1])

        if 0 <= x_min - key_xmax <= max_x_gap:  # 右边且不远
            if not (y_max < key_ymin or y_min > key_ymax + max_y_gap):  # y重叠或接近
                candidates.append(idx)

    if not candidates:
        return None

    # 按y排序 + 连续拼接
    candidates = sorted(candidates, key=lambda i: np.min(polys[i][:, 1]))
    merged_idxs = [candidates[0]]
    for idx in candidates[1:]:
        prev_idx = merged_idxs[-1]
        prev_ymax = np.max(polys[prev_idx][:, 1])
        curr_ymin = np.min(polys[idx][:, 1])
        if curr_ymin - prev_ymax <= max_y_gap:
            merged_idxs.append(idx)
        else:
            break

    # 拼接文本，平均置信度，记录box
    merged_text = "".join([texts[i] for i in merged_idxs])
    merged_text = correct_common_text_errors(merged_text)  # 自动纠错
    merged_score = np.mean([scores[i] for i in merged_idxs])
    merged_box = [polys[i].tolist() for i in merged_idxs]

    return {
        "box": merged_box,
        "text": merged_text,
        "score": merged_score
    }


def extract_keys_by_anchor(anchor_text, key_list, texts, polys, scores):
    """
    以锚点为基准，抽取其右侧最近的key及其对应value（支持多key）。
    参数说明：
        anchor_text: 锚点文本
        key_list: 需要抽取的key列表
        texts, polys, scores: OCR结果
    返回：
        dict，key为key_list中的每个key，value为拼接结果
    """
    # 找到锚点索引
    anchor_idx = None
    for idx, text in enumerate(texts):
        if text.strip() == anchor_text:
            anchor_idx = idx
            break
    if anchor_idx is None:
        print(f"未找到锚点：{anchor_text}")
        return {}

    result = {}
    for key in key_list:
        # 找到key索引（锚点右侧最近的key）
        anchor_box = polys[anchor_idx]
        anchor_xmax = np.max(anchor_box[:, 0])
        key_idx = None
        min_dist = float('inf')
        for idx, text in enumerate(texts):
            if text.strip() == key:
                box = polys[idx]
                x_min = np.min(box[:, 0])
                if x_min > anchor_xmax:
                    dist = x_min - anchor_xmax
                    if dist < min_dist:
                        min_dist = dist
                        key_idx = idx
        if key_idx is not None:
            value = robust_merge_multiline_value(key_idx, texts, polys, scores, key)
            if value and 'text' in value:
                value['text'] = correct_common_text_errors(value['text'])
            result[key] = value

        else:
            result[key] = None
    return result

def chinese_upper_to_num(upper_str):
    """
    支持常见中文大写金额转阿拉伯数字（如：'叁万贰仟陆佰叁拾肆元叁角肆分' -> 32634.34）
    参数：
        upper_str: 中文大写金额字符串
    返回：
        float，小写金额
    """
    cn_num = {'零': 0, '壹': 1, '赋': 2, '贰': 2, '式': 2, '叁': 3, '参': 3, '些': 3, '肆': 4, '伍': 5, '陆': 6,
              '吨': 6, '柒': 7, '染': 7,
              '捌': 8, '拟': 8, '玖': 9}
    cn_unit = {'拾': 10, '佰': 100, '循': 100, '仟': 1000, '万': 10000, '亿': 100000000}
    result = 0
    section = 0
    number = 0
    unit = 1
    upper_str = upper_str.replace('圆', '元')
    if '元' not in upper_str:
        upper_str += '元'
    integer_part, *decimal_part = upper_str.split('元')
    # 整数部分
    for c in integer_part:
        if c in cn_num:
            number = cn_num[c]
        elif c in cn_unit:
            unit = cn_unit[c]
            if unit == 10000 or unit == 100000000:
                section = (section + number) * unit
                result += section
                section = 0
            else:
                section += number * unit
            number = 0
        else:
            continue
    result += section + number
    # 小数部分
    decimal = 0.0
    if decimal_part:
        dec = decimal_part[0]
        jiao = dec.find('角')
        if jiao != -1:
            decimal += cn_num.get(dec[jiao-1], 0) * 0.1
        fen = dec.find('分')
        if fen != -1:
            decimal += cn_num.get(dec[fen-1], 0) * 0.01
    return round(result + decimal, 2)


def extract_fields_from_ocr(texts, polys, scores):
    """
    从 OCR 结果中抽取票据结构化字段
    返回字典 bill_data
    """
    bill_data = {}

    # 判断是否为特定票据
    ticket_flag = any("中国电建集团财务有限责任公司进账凭证" in t for t in texts)
    if not ticket_flag:
        print("非电建集团进账凭证，无法抽取。")
        return bill_data  # 返回空字典

    # 1. 抽取“交易流水号”
    key_text = "交易流水号："
    for idx, text in enumerate(texts):
        if key_text in text.strip():
            value = robust_merge_multiline_value(idx, texts, polys, scores, key_text)
            if value and value['text']:
                bill_data['transaction_no'] = value['text']
            break  # 找到第一个匹配即可

    # 2. 锚点“收款人”提取右边账号
    anchor_text = "收款人"
    key_list = ["账号"]
    res = extract_keys_by_anchor(anchor_text, key_list, texts, polys, scores)
    if res.get("账号") and res["账号"]["text"]:
        bill_data['payee_account'] = res["账号"]["text"]

    # 3. 锚点“付款人”提取多个字段
    anchor_text = "付款人"
    key_list = ["单位名称", "账号", "开户银行"]
    res = extract_keys_by_anchor(anchor_text, key_list, texts, polys, scores)
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
                value = robust_merge_multiline_value(idx, texts, polys, scores, key_text, max_x_gap=60)
                if value and value['text']:
                    bill_data['amount_upper'] = value['text']
                    bill_data['amount'] = chinese_upper_to_num(value['text'])
                break

    # 5. 提取“用途”
    key_text = "用途"
    for idx, text in enumerate(texts):
        if key_text in text.strip():
            value = robust_merge_multiline_value(idx, texts, polys, scores, key_text)
            if value and value['text']:
                bill_data['purpose'] = value['text']
            break

    return bill_data
