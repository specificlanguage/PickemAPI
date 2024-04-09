import datetime
import logging
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from sqlalchemy.orm import Session

from pickem.db.crud import games, users, picks, sessions
from pickem.db.schemas import Date
from pickem.lib.users import getUserIdByUsername
from pickem.dependencies import get_db, get_user

router = APIRouter(
    prefix="/picks",
    tags=["picks"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)

class PickEntry(BaseModel):
    gameID: int
    pickedHome: bool
    isSeries: bool
    comment: str | None = None

class MultiplePickEntry(BaseModel):
    picks: List[PickEntry]


@router.post("/session/new")
async def createSession(date: Date | None, response: Response, uid=Depends(get_user), db: Session = Depends(get_db)):
    """ Creates a list of picks for a current session (only for a specific day) """
    prefs = users.getUserPreferences(db, uid)
    if not date:
        today = date.today()
        date = Date(year=today.year, month=today.month, day=today.day)
    date = datetime.date(year=date.year, month=date.month, day=date.day)
    session = sessions.getSession(db, uid, date, prefs.selectionTiming != "daily")

    if session:  # Returns without creating a new session -- must keep unique constraint
        return session

    # Creates the session (and returns a 201 status code to indicate creation)
    gameOptions = games.getGamesByDate(db, date.year, date.month, date.day)
    if not gameOptions:
        raise HTTPException(404, detail="No games found for this date")
    newSess = sessions.createSession(db, uid, gameOptions,
                            is_series=prefs.selectionTiming != "daily",
                            favTeam=prefs.favoriteTeam_id)
    response.status_code = status.HTTP_201_CREATED
    return newSess


@router.get("/session")
async def getPickSession(year: int, month: int, day: int, uid=Depends(get_user), db: Session = Depends(get_db)):
    prefs = users.getUserPreferences(db, uid)
    date = datetime.date(year=year, month=month, day=day)
    session = sessions.getSession(db, uid, date, is_series=prefs.selectionTiming != "daily")
    if not session:
        raise HTTPException(404, detail="Session not found")
    return session


# TODO later: Date range (i.e. by week or by month)
@router.get("/leaderboard")
@cache(expire=60 * 60 * 4)
async def getLeaderboard(db: Session = Depends(get_db)):
    # Todo later: Discriminate by series
    leaderboard = picks.get_leaders(db, False)
    return {"leaders": [{
        "userID": userID,
        "correctPicks": correctPicks,
        "totalPicks": totalPicks,
    } for userID, correctPicks, totalPicks in leaderboard]}

@router.get("/date")
async def get_picks_by_date(year: int, month: int, day: int, uid=Depends(get_user), db: Session = Depends(get_db)):
    pickResults = picks.getPicksByUserDate(db, uid, year, month, day, False)
    response = []
    for gameID, pickedHome, isSeries, comment in pickResults:
        response.append({
            "gameID": gameID,
            "pickedHome": pickedHome,
            "isSeries": isSeries,
            "comment": comment
        })
    return response

@router.get("/all")
async def get_total_picks_multiple(isSeries: bool, gameID: Annotated[list[int], Query()] = [], db: Session = Depends(get_db)):
    """
    Gets the total number of picks, and the number of home picks and away picks for multiple specified games.
    :param gameIDs: Game IDs of the game to get picks for.
    :param isSeries: Whether the picks should be queried by series or not.
    :param db: Session to use.
    :return:
    """
    gameResults = []
    for gid in gameID:
        ans = picks.getTotalPicksForGame(db, gid, isSeries)
        if not ans:
            raise HTTPException(404, detail="Game not found")
        gameResults.append({
            "game_id": gid,
            "totalPicks": ans[0],
            "homePicks": ans[1],
            "awayPicks": ans[2],
        })
    return {"results": gameResults}


@router.get("/user/history")
async def get_user_picks(
        uid: str | None = None,
        username: str | None = None,
        db: Session = Depends(get_db),
        offset: int = 0):
    """
    Gets the historical picks for a user. given a username or a user id, optionally an offset if all exhausted.
    :param uid: User id to retrieve.
    :param username: Username to retrieve. This is slightly slower since it need to obtain a userID from cache.
    Returns list of picks.
    """
    if not uid and not username:
        raise HTTPException(404, detail="User not found or not provided")
    if uid:
        dbResp = picks.getUserPickHistory(db, uid, offset=offset)
        return dbResp
    if username:
        userId = getUserIdByUsername(username)
        dbResp = picks.getUserPickHistory(db, userId, offset=offset)
        return dbResp


@router.get("/{gameID}/all")
async def get_total_picks(gameID: int, isSeries: bool, db: Session = Depends(get_db)):
    """
    Gets the total number of picks, and the number of home picks and away picks for a certain game.
    **gameID**: Game ID of the game to get picks for.
    **isSeries**: Whether the picks should be queried by series or not.
    :return: Object containing gameID, total picks, home picks, and away picks.
    """
    ans = picks.getTotalPicksForGame(db, gameID, isSeries)
    if not ans:
        raise HTTPException(404, detail="Game not found")
    return {
        "game_id": gameID,
        "totalPicks": ans[0],
        "homePicks": ans[1],
        "awayPicks": ans[2],
    }


@router.get("/{gameID}")
async def get_pick(gameID: int, uid=Depends(get_user), db: Session = Depends(get_db)):
    """
    Gets the pick for a certain game for a certain user.
    Requires authentication.
    - **gameID**: The ID of the game to pick
    """
    pick = picks.get_pick(db, uid, gameID)
    if not pick:
        raise HTTPException(404, detail="Pick not found")
    return {
        "gameID": gameID,
        "pickedHome": pick.pickedHome,
        "isSeries": pick.is_series,
        "comment": pick.comment
    }


@router.post("/{gameID}")
async def set_pick(pick: PickEntry, response: Response, uid=Depends(get_user), db: Session = Depends(get_db), ):
    """
    Sets the pick for a certain game (created) by a certain user, and associates it with each game.
    Requires authentication.
    - **gameID**: The ID of the game to pick
    - **pickedHome**: Whether the user picked the home team in the game
    - **isSeries**: Whether the user is picking for the series of games, rather than the individual game
    Returns the Pick object that was created.
    """
    try:

        pickObj = picks.get_pick(db, uid, pick.gameID)

        if pickObj:  # Pick already exists, just update instead of inserting.
            return picks.update_pick(db, uid, pick.gameID, pick.pickedHome, pick.isSeries, pick.comment if pick.comment else "")

        # Creates pick.
        pickObj = picks.create_pick(db, uid,
                                 pick.gameID,
                                 pick.pickedHome,
                                 pick.isSeries,
                                 pick.comment if pick.comment else "")  # Comment optional.

        response.status_code = status.HTTP_201_CREATED
        return pickObj
    except Exception as e:
        logging.warning(e)
        raise HTTPException(500, detail="Internal service error")


@router.post("/")
async def set_multiple_picks(pickList: MultiplePickEntry, uid=Depends(get_user), db: Session = Depends(get_db)):
    """
    Sets multiple picks for multiple games -- has same functionality as set_pick, but for multiple games. Requires authentication.
    **picks**: List of picks to set.
    Returns pick object created.
    """
    try:
        picks.create_picks(db, uid, pickList.picks)
        return {"message": "Picks created"}
    except Exception as e:
        logging.warning(e)
        raise HTTPException(500, detail="Internal service error")


