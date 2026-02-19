from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routers import upload, generate

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(title="Heritage AI - Family History Narrative", lifespan=lifespan)

app.include_router(upload.router)
app.include_router(generate.router)

@app.get("/")
async def root():
    return {"message": "Heritage AI API ready"}