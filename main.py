from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from routers import games
from db.alchemy import SessionLocal, get_db
from db import crud

load_dotenv()
app = FastAPI()

app.include_router(games.router)


@app.get("/")
async def root():
    return {"app": "Pick'em API",
            "version": "0.0.1 alpha"}


@app.get("/teams")
async def getTeams(id: int | None = None, abbr: str | None = None, db: Session = Depends(get_db)):
    if id:
        return crud.getTeam(db, id)
    if abbr:
        return crud.getTeamByAbbr(db, abbr)
    return crud.getAllTeams(db)
