from sqlalchemy.orm import Session
from app.models.record import Record

def create_record(db: Session, filename: str, text: str):
    record = Record(filename=filename, result_text=text)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_record(db: Session, record_id: int):
    return db.query(Record).filter(Record.id == record_id).first()
