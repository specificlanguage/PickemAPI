from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from routers import games, picks
from db.alchemy import SessionLocal
from dependencies import get_db
from db import crud

load_dotenv()
app = FastAPI()

app.include_router(games.router)
app.include_router(picks.router)

# TODO use env variables depending on env
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
