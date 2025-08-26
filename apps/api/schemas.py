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
