from sqlalchemy.orm import Session
from pickem.db import models
from pickem.db import schemas
import httpx

from pickem.db.alchemy import SessionLocal

SEASON = 2024
AL_ID, NL_ID = 103, 104

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

def create_team(db: Session, team: schemas.TeamCreate):
    db_team = models.Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

def loadTeams():
    with httpx.Client() as client:
        # American League first
        r = client.get("https://statsapi.mlb.com/api/v1/teams?season={0}&leagueIds={1},{2}".format(SEASON, AL_ID, NL_ID))
        resp = r.json()
    for team in resp['teams']:
        teamObj = schemas.TeamCreate(
            id=team["id"],
            name=team["name"],
            cityName=team["locationName"],
            teamName=team["teamName"],
            logo="",
            abbr=team["abbreviation"]
        )
        print("creating {0} ({1})".format(teamObj.name, teamObj.id))
        create_team(db, teamObj)


loadTeams()
