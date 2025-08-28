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

# User model for authentication
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # 'user' or 'admin'
