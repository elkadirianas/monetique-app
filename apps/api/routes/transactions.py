from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from db import get_db

router = APIRouter()

@router.get("/transactions", response_model=list[schemas.Transaction])
def get_transactions(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.FactTransaction).order_by(models.FactTransaction.ts.desc()).limit(limit).all()
