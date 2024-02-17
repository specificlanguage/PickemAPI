import datetime
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from pickem.db.crud import games, users, picks, sessions
from pickem.db.schemas import Date
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
        "gameID": gameID,
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


