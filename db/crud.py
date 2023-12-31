import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased
from . import models, schemas

def cleanupGameArraysWithTeams(games):
    for game, homeName, awayName in games:
        game.homeName = homeName
        game.awayName = awayName
    return [game for game, _, _ in games]

def getAllTeams(db: Session):
    return db.query(models.Team).all()

def getTeam(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()

def getTeamByAbbr(db: Session, abbr: str):
    return db.query(models.Team).filter(models.Team.abbr == abbr).first()


def getGame(db: Session, gameID: int):
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    game, homeTeamName, awayTeamName = (db.query(models.Game, homeTeam.teamName, awayTeam.teamName)
        .join(homeTeam, onclause=homeTeam.id == models.Game.homeTeam_id)
        .join(awayTeam, onclause=awayTeam.id == models.Game.awayTeam_id)
        .filter(models.Game.id == gameID)
        .first())
    game.homeName = homeTeamName
    game.awayName = awayTeamName
    return game


def getGamesWithTeams(db: Session, team1_id: int, team2_id: int):
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    return cleanupGameArraysWithTeams(
        db.query(models.Game, homeTeam.teamName, awayTeam.teamName)
            .join(homeTeam, onclause=homeTeam.id == models.Game.homeTeam_id)
            .join(awayTeam, onclause=awayTeam.id == models.Game.awayTeam_id)
            .filter(
                (models.Game.homeTeam_id == team1_id and models.Game.awayTeam_id == team2_id) or
                (models.Game.homeTeam_id == team2_id and models.Game.awayTeam_id == team1_id)
    ).all())


def getGamesWithAbbr(db: Session, team1_abbr: str, team2_abbr: str):
    subquery = db.query(models.Team.id).where(models.Team.abbr.in_([team1_abbr, team2_abbr]))
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    return cleanupGameArraysWithTeams(db.query(models.Game, homeTeam.teamName, awayTeam.teamName)
            .join(homeTeam, onclause=homeTeam.id == models.Game.homeTeam_id)
            .join(awayTeam, onclause=awayTeam.id == models.Game.awayTeam_id)
            .filter(models.Game.homeTeam_id.in_(subquery))
            .filter(models.Game.awayTeam_id.in_(subquery))
            .order_by(models.Game.startTimeUTC)
            .all())

def getGameByDate(db: Session, year: int, month: int, day: int):
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    return cleanupGameArraysWithTeams(db.query(models.Game, homeTeam.teamName, awayTeam.teamName)
                .join(homeTeam, onclause=homeTeam.id == models.Game.homeTeam_id)
                .join(awayTeam, onclause=awayTeam.id == models.Game.awayTeam_id)
                .filter(models.Game.date == datetime.date(year, month, day))
                .all()
    )
