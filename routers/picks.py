import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db, get_firebase_user
from db.crud.picks import getTotalPicksForGame, createPickForGame

router = APIRouter(
    prefix="/picks",
    tags=["picks"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


@router.get("/{gameID}")
async def getTotalPicks(gameID: int, db: Session = Depends(get_db)):
    ans = getTotalPicksForGame(db, gameID)
    if not ans:
        raise HTTPException(404, detail="Game not found")
    return {
        "gameID": gameID,
        "totalPicks": ans[0],
        "homePicks": ans[1],
        "awayPicks": ans[2],
    }


@router.post("")
async def setPick(gameID: int, pickedHome: bool, user=Depends(get_firebase_user), db: Session = Depends(get_db)):
    try:
        createPickForGame(db, user["uid"], gameID, pickedHome)
    except Exception as e:
        logging.warning(e)
        raise HTTPException(500, detail="Internal service error")