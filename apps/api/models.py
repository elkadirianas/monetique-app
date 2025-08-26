from sqlalchemy import Column, Integer, String, Float, DateTime
from db import Base

class FactTransaction(Base):
    __tablename__ = "fact_transactions"

    id = Column(Integer, primary_key=True, index=True)
    iface = Column(String, index=True)
    ts = Column(DateTime)
    status = Column(String)
    amount = Column(Float)
    etl_loaded_at = Column(DateTime)
