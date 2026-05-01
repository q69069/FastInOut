from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, func
from database import Base


class BankStatement(Base):
    __tablename__ = "bank_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_account = Column(String(30))  # 银行账号
    statement_date = Column(Date)  # 对账日期
    description = Column(String(200))  # 摘要
    debit = Column(Float, default=0)  # 支出
    credit = Column(Float, default=0)  # 收入
    matched = Column(Boolean, default=False)  # 是否已匹配
    matched_id = Column(Integer)  # 匹配的收付款ID
    matched_type = Column(String(20))  # receipt/payment
    remark = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
