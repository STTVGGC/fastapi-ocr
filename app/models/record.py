from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    result_text = Column(String(2000))
    created_at = Column(DateTime, default=datetime.utcnow)
