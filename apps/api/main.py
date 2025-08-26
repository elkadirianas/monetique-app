from fastapi import FastAPI
# from .routes import transactions, stats
from routes import transactions, stats   # remove the dot


app = FastAPI(title="Monitoring API")

app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
