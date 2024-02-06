import logging, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from pickem.db.crud import games, users, picks
from pickem.db.crud.sessions import createSession, getSession
from pickem.db.schemas import Date
from pickem.dependencies import get_db, get_user

router = APIRouter(
    prefix="/picks",
    tags=["picks"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


@router.post("/session/new")
async def createSession(date: Date | None, response: Response, uid=Depends(get_user), db: Session = Depends(get_db)):
    """ Creates a list of picks for a current session (only for a specific day) """
    prefs = users.getUserPreferences(db, uid)
    if not date:
        today = date.today()
        date = Date(year=today.year, month=today.month, day=today.day)
    date = datetime.date(year=date.year, month=date.month, day=date.day)
    session = getSession(db, uid, date, prefs.selectionTiming != "daily")

    if session:  # Returns without creating a new session -- must keep unique constraint
        return session

    # Creates the session (and returns a 201 status code to indicate creation)
    gameOptions = games.getGamesByDate(db, date.year, date.month, date.day)
    if not gameOptions:
        raise HTTPException(404, detail="No games found for this date")
    session = createSession(db, uid, gameOptions,
                            is_series=prefs.selectionTiming != "daily",
                            favTeam=prefs.favTeam)
    session["created"] = True
    response.status_code = status.HTTP_201_CREATED
    return session


@router.get("/session")
async def getPickSession(year: int, month: int, day: int, uid=Depends(get_user), db: Session = Depends(get_db)):
    prefs = users.getUserPreferences(db, uid)
    date = datetime.date(year=year, month=month, day=day)
    session = getSession(db, uid, date, is_series=prefs.selectionTiming != "daily")
    if not session:
        raise HTTPException(404, detail="Session not found")
    return session

@router.get("/{gameID}")
async def getTotalPicks(gameID: int, db: Session = Depends(get_db)):
    ans = picks.getTotalPicksForGame(db, gameID)
    if not ans:
        raise HTTPException(404, detail="Game not found")
    return {
        "gameID": gameID,
        "totalPicks": ans[0],
        "homePicks": ans[1],
        "awayPicks": ans[2],
    }

# TODO: configure Clerk information
# @router.post("")
# async def setPick(gameID: int, pickedHome: bool, user=Depends(get_firebase_user), db: Session = Depends(get_db)):
#     try:
#         createPickForGame(db, user["uid"], gameID, pickedHome)
#     except Exception as e:
#         logging.warning(e)
#         raise HTTPException(500, detail="Internal service error")
