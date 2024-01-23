import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from pickem.db import models


def getPicksByUserDate(db: Session, userID: str, year: int, month: int, day: int):
    return (db.query(models.Pick.game_id, models.Pick.pickedHome, models.Game.date, models.Game.id, models.Game.homeTeam, models.Game.awayTeam)
            .join(models.Game, onclause=models.Game.id == models.Pick.game_id)
            .filter(models.Pick.user_id == userID)
            .filter(models.Game.date == datetime.date(year, month, day))
            .all())


def getPicksByUser(db: Session, userID: str):
    return db.query(models.Pick).join(models.Pick.user_id == userID).all()


def getTotalPicksForGame(db: Session, gameID: int):
    subquery = (db.query(func.count("*"))
                .where(models.Pick.game_id == gameID and models.Pick.pickedHome)
                .scalar_subquery())
    return (db.query(
                func.count("*").label("total"),
                subquery.label("home_picks"),
                (func.count("*") - subquery).label("away_picks"))
            .where(models.Pick.game_id == gameID).first())


def createPickForGame(db: Session, userID: str, gameID: int, pickedHome: bool, comment: str = ""):
    pick = models.Pick(
        userID=userID,
        gameID=gameID,
        pickedHome=pickedHome,
        comment=comment
    )
    db.add(pick)
    db.commit()
    db.refresh(pick)

