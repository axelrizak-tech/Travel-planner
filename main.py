from fastapi import FastAPI
app = FastAPI()

from database import engine
from models import Base
from routers import router
app.include_router(router)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Planner API")

app.include_router(router)
