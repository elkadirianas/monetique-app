from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):
    id: int
    iface: str
    ts: datetime
    status: str
    amount: float
    etl_loaded_at: datetime

    class Config:
        orm_mode = True

# User schema for authentication
class UserBase(BaseModel):
    username: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True
