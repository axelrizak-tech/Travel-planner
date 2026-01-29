from fastapi import FastAPI
from database import engine, Base
from routers import router as api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Planner API",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Travel Planner API is running"}
