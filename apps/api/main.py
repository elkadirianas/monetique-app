from fastapi import FastAPI
# from .routes import transactions, stats

from routes import transactions, stats, auth


app = FastAPI(title="Monitoring API")

app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
