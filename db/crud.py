from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models, schemas

def getAllTeams(db: Session):
    return db.query(models.Team).all()

def getTeam(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()

def getTeamByAbbr(db: Session, abbr: str):
    return db.query(models.Team).filter(models.Team.abbr == abbr).first()


def getGame(db: Session, gameID: int):
    return db.query(models.Game).filter(models.Game.id == gameID).first()


def getGamesWithTeams(db: Session, team1_id: int, team2_id: int):
    return db.query(models.Game).filter(
        (models.Game.homeTeam_id == team1_id and models.Game.awayTeam_id == team2_id) or
        (models.Game.homeTeam_id == team2_id and models.Game.awayTeam_id == team1_id)
    ).all()


def getGamesWithAbbr(db: Session, team1_abbr: str, team2_abbr: str):
    subquery = db.query(models.Team.id).where(models.Team.abbr.in_([team1_abbr, team2_abbr]))
    return (db.query(models.Game)
            .filter(models.Game.homeTeam_id.in_(subquery))
            .filter(models.Game.awayTeam_id.in_(subquery))
            .order_by(models.Game.startTimeUTC)
            .all())