from sqlalchemy.orm import Session
from pickem.db import models


def getAllTeams(db: Session): # noqa: E501
    return db.query(models.Team).all()

def getTeamByID(db: Session, id: int):
    return db.query(models.Team).filter(models.Team.id == id).first()

def getTeamByAbbr(db: Session, abbr: str):
    return db.query(models.Team).filter(models.Team.abbr == abbr).first()