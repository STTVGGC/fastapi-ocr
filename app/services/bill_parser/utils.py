# services/bill_parser/utils.py
# merge + 错字修复
import numpy as np

def correct_text(text: str):
    corrections = {
        "项自经理部": "项目经理部",  # OCR常识别错误
        "，勿重复记账使用。": "",  # 清理无关信息
        "参": "叁",  # 误识别的中文数字
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text


def merge_right_value(key_idx, texts, polys, scores, key_text,
                      max_y_gap=10, max_x_gap=200):
    """
    提取 key 右边多行 value 的通用函数
    """
    key_box = polys[key_idx]
    key_xmax = np.max(key_box[:, 0])
    key_ymin = np.min(key_box[:, 1])
    key_ymax = np.max(key_box[:, 1])

    candidates = []
    for idx, t in enumerate(texts):
        if idx == key_idx:
            continue
        box = polys[idx]
        x_min = np.min(box[:, 0])
        y_min = np.min(box[:, 1])
        y_max = np.max(box[:, 1])

        if 0 <= x_min - key_xmax <= max_x_gap:
            if not (y_max < key_ymin or y_min > key_ymax + max_y_gap):
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
    merged_text = correct_text(merged_text)  # 自动纠错
    merged_score = np.mean([scores[i] for i in merged_idxs])
    merged_box = [polys[i].tolist() for i in merged_idxs]

    return {
        "box": merged_box,
        "text": merged_text,
        "score": merged_score
    }


def find_key_value(anchor, key_list, texts, polys, scores):
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
    # 找 anchor
    anchor_idx = None
    for idx, text in enumerate(texts):
        if text.strip() == anchor:
            anchor_idx = idx
            break
    if anchor_idx is None:
        print(f"未找到锚点：{anchor}")
        return {}

    anchor_xmax = np.max(polys[anchor_idx][:, 0])
    result = {}

    for key in key_list:
        min_dist = float('inf')
        key_idx = None

        # 找锚点右侧最近 key
        for i, t in enumerate(texts):
            if t.strip() == key:
                x_min = np.min(polys[i][:, 0])
                if x_min > anchor_xmax and (x_min - anchor_xmax) < min_dist:
                    min_dist = x_min - anchor_xmax
                    key_idx = i

        if key_idx is not None:
            val = merge_right_value(key_idx, texts, polys, scores, key)
            if val:
                val["text"] = correct_text(val["text"])
            result[key] = val
        else:
            result[key] = None

    return result
