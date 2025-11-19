#pydantic

from pydantic import BaseModel

class BillUpdate(BaseModel):
    id:int  # 主键 ID
    purpose:str                        # 用途，例如：支付XXXX费用
    transaction_no:str                # 交易流水号
    amount_upper :str                   # 金额（大写）
    amount:float                               # 金额（数字）
    payer :str=None                         # 付款人名称
    payer_account :str=None                # 付款人账号
    payer_bank :str=None                  # 付款人开户行
    payee :str=None                        # 收款人名称
    payee_account :str=None                # 收款人账号
    payee_bank :str=None                   # 收款人开户行

    model_config = {
        "from_attributes": True
    }
