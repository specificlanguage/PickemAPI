import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased
from pickem.db import models, schemas


def getGameBaseQuery(db: Session):
    """ This is the generic query that gets a game, but also with its team names,
    it should be used for context for every query to fetch a game."""
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    return (db.query(models.Game, homeTeam.teamName, awayTeam.teamName)
            .join(homeTeam, onclause=homeTeam.id == models.Game.homeTeam_id)
            .join(awayTeam, onclause=awayTeam.id == models.Game.awayTeam_id))


def cleanupGameArraysWithTeams(games):
    """This cleans up the game queries with multiple results to be able to easily parse into a JSON-format."""
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


async def getGame(db: Session, gameID: int) -> models.Game | None:
    try:
        game, homeTeamName, awayTeamName = (await getGameBaseQuery(db)
                                            .filter(models.Game.id == gameID)
                                            .first())
        game.homeName = homeTeamName
        if game is not None:
            game.awayName = awayTeamName
            return game
    except TypeError as e:
        return None

def getGamesWithTeams(db: Session, team1_id: int, team2_id: int):
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    return cleanupGameArraysWithTeams(
        getGameBaseQuery(db)
        .filter(
            (models.Game.homeTeam_id == team1_id and models.Game.awayTeam_id == team2_id) or
            (models.Game.homeTeam_id == team2_id and models.Game.awayTeam_id == team1_id)
        ).all())


def getGamesWithAbbr(db: Session, team1_abbr: str, team2_abbr: str):
    subquery = db.query(models.Team.id).where(models.Team.abbr.in_([team1_abbr, team2_abbr]))
    return cleanupGameArraysWithTeams(
        getGameBaseQuery(db)
        .filter(models.Game.homeTeam_id.in_(subquery))
        .filter(models.Game.awayTeam_id.in_(subquery))
        .order_by(models.Game.startTimeUTC)
        .all())


def getGamesByDate(db: Session, year: int, month: int, day: int):
    return cleanupGameArraysWithTeams(
        getGameBaseQuery(db)
        .filter(models.Game.date == datetime.date(year, month, day))
        .all()
    )

def getGamesByIDs(db: Session, gameIDs: List[int]):
    return cleanupGameArraysWithTeams(getGameBaseQuery(db).filter(models.Game.id.in_(gameIDs)).all())