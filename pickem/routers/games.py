from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from redis import Redis
from sqlalchemy.orm import Session

from pickem.dependencies import get_db, get_redis
from pickem.db.crud import series, games
from pickem.lib.status import retrieveStats

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


@router.get("/teams")
async def get_games_with_teams(team1_abbr: str | None = None,
                               team2_abbr: str | None = None,
                               team1_id: int | None = None,
                               team2_id: int | None = None,
                               db: Session = Depends(get_db)):
    if team1_id is None or team2_id is None:
        if team1_abbr is None or team2_abbr is None:
            raise HTTPException(status_code=400, detail=
            "Either team1_id/team2_id must be specified, or team1_abbr/team2_abbr.")
        gamesInfo = games.getGamesWithAbbr(db, team1_abbr, team2_abbr)
        return gamesInfo

    return games.getGamesWithTeams(db, team1_id, team2_id)


@router.get("/date")
async def get_game_by_date(year: int, month: int, day: int, db: Session = Depends(get_db)):
    return games.getGamesByDate(db, year, month, day)


@router.get("/series/seriesNums")
async def get_series_nums():
    return series.getSeriesNums()


@router.get("/series")
async def get_game_by_series(seriesNum: int, db: Session = Depends(get_db)):
    games = series.getGamesBySeries(db, seriesNum)
    if len(games) == 0:
        raise HTTPException(status_code=404, detail="No games for this series number")
    return games


@router.get("/status/date")
async def get_game_status(year: int, month: int, day: int, redis: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    """
    Returns the current status of the games on the given date, usually in the form of:
    Please note that due to limitations on Redis cache, all fields are returned as strings.
    {
        status: "COMPLETED" | "SCHEDULED" | "IN_PROGRESS",
        gameID: int
    }

    For completed and in progress games the following two fields are added:
    `homeScore: int` and `awayScore: int`

    For scheduled games the following field is added:
    `startTimeUTC: datetime`

    For in-progress (and live games < 24 hours completed), all fields below are added:
    `homeScore: int`, `awayScore: int`,
    `currentInning: int`, `currentPitcher: str`, `atBat: str`
    `isTopInning: int`, `outs: int`, `onFirst: int`, `onSecond: int`, `onThird: int`
    Please note that the last five fields are 0 or 1, representing booleans.
    """
    response = []
    gameObjs = games.getGamesByDate(db, year, month, day)
    gameIDs = [gameObj.id for gameObj in gameObjs]

    needsDBQuery = set(gameIDs)
    for gid in gameIDs:
        stats = await retrieveStats(gid, redis)
        if not stats.get("error"):
            needsDBQuery.remove(gid)
            response.append(stats)

    # Live stats not available for all items still in needsDBQuery, which means either scheduled or completed, must query the database.
    gameObjs = games.getGamesByIDs(db, list(needsDBQuery))
    for gameObj in gameObjs:
        currStatus = "COMPLETED" if gameObj.finished else "SCHEDULED"
        if gameObj.winner == None and gameObj.finished:
            currStatus = "POSTPONED"
        statusObj = {
            "status": currStatus,
            "gameID": gameObj.id,
        }
        if statusObj["status"] == "SCHEDULED":
            statusObj["startTimeUTC"] = gameObj.startTimeUTC
        if statusObj["status"] == "COMPLETED" or statusObj["status"] == "POSTPONED":
            statusObj["home_score"] = gameObj.home_score
            statusObj["away_score"] = gameObj.away_score
        response.append(statusObj)

    return response




@router.get("/status")
async def get_game_status(gameID: int, redis: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    """ Returns the current status of one single game, usually in the form of:
        Please note that due to limitations on Redis cache, all fields are returned as strings.
        {
            status: "COMPLETED" | "SCHEDULED" | "IN_PROGRESS",
            gameID: int
        }

        For completed and in progress games the following two fields are added:
        `homeScore: int` and `awayScore: int`

        For scheduled games the following field is added:
        `startTimeUTC: datetime`

        For in-progress (and live games < 24 hours completed), all fields below are added:
        `homeScore: int`, `awayScore: int`,
        `currentInning: int`, `currentPitcher: str`, `atBat: str`
        `isTopInning: int`, `outs: int`, `onFirst: int`, `onSecond: int`, `onThird: int`
        Please note that the last five fields are 0 or 1, representing booleans.
    """

    stats = await retrieveStats(gameID, redis)
    if not stats.get("error"):
        return stats

    # Live stats not available for all items still in needsDBQuery, which means either scheduled or completed,
    # must query the database.
    gameObjs = games.getGamesByIDs(db, [gameID])
    for gameObj in gameObjs:
        currStatus = "COMPLETED" if gameObj.finished else "SCHEDULED"
        if gameObj.winner == None and gameObj.finished:
            currStatus = "POSTPONED"
        statusObj = {
            "status": currStatus,
            "gameID": gameObj.id,
        }
        if statusObj["status"] == "SCHEDULED":
            statusObj["startTimeUTC"] = gameObj.startTimeUTC
        if statusObj["status"] == "COMPLETED" or statusObj["status"] == "POSTPONED":
            statusObj["homeScore"] = gameObj.home_score
            statusObj["awayScore"] = gameObj.away_score
        return statusObj


@router.get("/{id}")
async def get_game(id: str, db: Session = Depends(get_db)):
    game = await games.getGame(db, int(id))
    if not game:
        raise HTTPException(status_code=404, detail="Game does not exist")
    return game