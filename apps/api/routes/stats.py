from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
from db import get_db

router = APIRouter()

@router.get("/stats/summary")
def get_summary(db: Session = Depends(get_db)):
    total = db.query(func.count(models.FactTransaction.id)).scalar()
    accepted = db.query(func.count()).filter(models.FactTransaction.status=="ACCEPTED").scalar()
    rejected = db.query(func.count()).filter(models.FactTransaction.status.like("REJECT%")).scalar()
    return {
        "total": total,
        "accepted": accepted,
        "rejected": rejected,
        "reject_rate": (rejected/total*100 if total>0 else 0)
    }
