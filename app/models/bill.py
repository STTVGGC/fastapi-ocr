# app/models/bill.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

# 票据数据表模型（ORM 模型）
# 每个类 = 数据库中的一张表
class Bill(Base):
    __tablename__ = "bills"  # 数据库中的表名 = bills

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)  # 主键 ID
    purpose = Column(String(255))                       # 用途，例如：支付XXXX费用
    transaction_no = Column(String(255),unique=True)                # 交易流水号
    amount_upper = Column(String(255))                  # 金额（大写）
    amount = Column(Float)                              # 金额（数字）
    payer = Column(String(255))                         # 付款人名称
    payer_account = Column(String(100))                 # 付款人账号
    payer_bank = Column(String(255))                    # 付款人开户行
    payee = Column(String(255))                         # 收款人名称
    payee_account = Column(String(100))                 # 收款人账号
    payee_bank = Column(String(255))                    # 收款人开户行
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间（自动记录）

