from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend # TODO later: use Redis
from fastapi_cache.decorator import cache
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from pickem.routers import games, picks
from pickem.dependencies import get_db
from pickem.db.crud import teams

load_dotenv()
app = FastAPI()

app.include_router(games.router)
app.include_router(picks.router)

# TODO use env variables depending on env
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"app": "Pick'em API",
            "version": "0.0.1 alpha"}


@app.get("/teams")
@cache(expire=1000000)  # We don't need to retrieve this data from the database very often, if at all.
async def getTeams(id: int | None = None, abbr: str | None = None, db: Session = Depends(get_db)):
    if id:
        return teams.getTeamByID(db, id)
    if abbr:
        return teams.getTeamByAbbr(db, abbr)
    return teams.getAllTeams(db)

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="pickem")
