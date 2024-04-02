from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend # TODO later: use Redis
from fastapi_cache.decorator import cache
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import httpx

from pickem.routers import games, picks, users
from pickem.dependencies import get_db
from pickem.db.crud import teams

load_dotenv()
app = FastAPI()

app.include_router(games.router)
app.include_router(picks.router)
app.include_router(users.router)

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

@app.get("/teams/standings")
@cache(expire=60 * 60 * 3)  # Retrieve new stats only a few times a day.
async def getTeamRecords():
    resp =httpx.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2024&standingTypes=regularSeason&hydrate=division,conference,sport,league,team,")
    standingGroups = {"standings": [], "teams": {}}  # Want to return standings by division as well as by team
    for standingGroup in resp.json()["records"]:
        standingObj = {"name": standingGroup["division"]["name"], "teams": []}
        for team in standingGroup["teamRecords"]:  # Parse the info from MLB's response
            teamObj = {
                "id": team["team"]["id"],
                "name": team["team"]["name"],
                "abbr": team["team"]["abbreviation"],
                "wins": team["wins"],
                "losses": team["losses"],
                "winningPercentage": team["winningPercentage"],
            }
            standingObj["teams"].append(teamObj)
            standingGroups["teams"][teamObj["id"]] = teamObj
        standingGroups["standings"].append(standingObj)
    return standingGroups



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
