from fastapi import FastAPI
from dotenv import load_dotenv

from db.alchemy import SessionLocal

load_dotenv()
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"app": "Pick'em API",
            "version": "0.0.1 alpha"}