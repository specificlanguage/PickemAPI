from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.alchemy import get_db
from db.picks_crud import getTotalPicksForGame

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