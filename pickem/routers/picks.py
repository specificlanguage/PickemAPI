import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pickem.lib.sessions import createSession
from pickem.db.crud import games, users, picks
from pickem.db.schemas import Date
from pickem.dependencies import get_db, get_user

router = APIRouter(
    prefix="/picks",
    tags=["picks"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


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

@router.post("session/new")
async def getSessionPicks(date: Date | None, uid = Depends(get_user), db: Session = Depends(get_db)):
    """ Creates a list of picks for a current session (only for a specific day) """
    prefs = users.getUserPreferences(db, uid)
    favTeam = prefs.favoriteTeam_id

    if not date:
        today = date.today()
        date = Date(year=today.year, month=today.month, day=today.day)

    gameOptions = games.getGamesByDate(db, date.year, date.month, date.day)
    if not gameOptions:
        raise HTTPException(404, detail="No games found for this date")

    sessionGames =


# TODO: configure Clerk information
# @router.post("")
# async def setPick(gameID: int, pickedHome: bool, user=Depends(get_firebase_user), db: Session = Depends(get_db)):
#     try:
#         createPickForGame(db, user["uid"], gameID, pickedHome)
#     except Exception as e:
#         logging.warning(e)
#         raise HTTPException(500, detail="Internal service error")