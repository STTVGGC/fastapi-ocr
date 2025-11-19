# services/bill_parser/amount_converter.py

def chinese_to_num(upper_str: str) -> float:
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