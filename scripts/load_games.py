from sqlalchemy import select
from sqlalchemy.orm import Session
from db import models, schemas
from datetime import datetime
import httpx

from db.alchemy import SessionLocal

SEASON = 2024
AL_ID, NL_ID = 103, 104

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_game(db: Session, game: schemas.GameCreate):
    db_team = models.Game(**game.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)

def createGameObject(game):
    return schemas.GameCreate(
        id=game["gamePk"],
        date=datetime.strptime(game["officialDate"], "%Y-%m-%d"),
        startTimeUTC=datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ"),
        venue=game["venue"]["name"],
        homeTeam_id=game["teams"]["home"]["team"]["id"],
        awayTeam_id=game["teams"]["away"]["team"]["id"],
        finished=False
    )

with next(get_session()) as session:
    statement = select(models.Team)
    teams = session.scalars(select(models.Team)).all()

with (httpx.Client() as client):
    for team in teams:
        print("loading games for", team.teamName)
        dates = client.get("https://statsapi.mlb.com/api/v1/schedule/?sportId=1&season={0}&scheduleTypes=games&teamId={1}&startDate=2024-03-28&endDate=2024-09-29".format(SEASON, team.id)).json()["dates"]
        for dateObj in dates:
            date = dateObj["date"]
            for game in dateObj["games"]:
                exists = session.scalars(select(models.Game).filter_by(id=game["gamePk"])).one_or_none()
                if exists is None:
                    print("processing {0} ({1})".format(game["gamePk"], game["officialDate"]))
                    gameObj = createGameObject(game)
                    create_game(session, gameObj)