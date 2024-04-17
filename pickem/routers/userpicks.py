from datetime import datetime, timedelta
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException

from pickem.db.crud import picks
from pickem.db.models import Session
from pickem.dependencies import get_db
from pickem.lib.users import getUserIdByUsername

# This router will be under the users router as before. The path to all endpoints below are "/picks/users/*"
router = APIRouter(
    prefix="/user",
    tags=["picks"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)

class RecordLookup(str, Enum):
    """
    Enum for the record lookup endpoint.
    """
    all = "all"
    week = "week"
    month = "month"

@router.get("/history")
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
    if not uid and username:
        uid = getUserIdByUsername(username)
    dbResp = picks.getUserPickHistory(db, uid, offset=offset)
    return [{
        "userID": row["user_id"],
        "gameID": row["game_id"],
        "pickedHome": row["pickedHome"],
        "isSeries": row["is_series"],
        "isSession": row["inSession"],
        "correct": row["correct"],
        "game": {
            "id": row["game_id"],
            "homeTeam_id": row["homeTeam_id"],
            "awayTeam_id": row["awayTeam_id"],
            "date": row["date"],
            "finished": row["finished"],
            "winner": row["winner"],
            "startTimeUTC": row["startTimeUTC"],
            "isMarquee": row["is_marquee"],
            "home_score": row["home_score"],
            "away_score": row["away_score"],
        }
    } for row in dbResp]


@router.get("/record")
async def getUserRecord(
        range: RecordLookup,
        userID: str | None = None,
        username: str | None = None,
        db: Session = Depends(get_db)):
    """
    Gets the historical record for a user. given a username or a user id.
    :param uid: User id to retrieve.
    :param username: Username to retrieve. This is slightly slower since it need to obtain a userID from cache.
    Returns list of picks.
    """
    if not userID and not username:
        raise HTTPException(404, detail="User not found or not provided")
    if not userID and username:
        userID = getUserIdByUsername(username)
    dbResp = None
    if range is RecordLookup.all:
        dbResp = picks.getUserRecord(db, userID)
    elif range is RecordLookup.week:
        dbResp = picks.getUserRecord(db, userID, before=datetime.now() - timedelta(days=7))
    elif range is RecordLookup.month:
        dbResp = picks.getUserRecord(db, userID, before=datetime.now() - timedelta(days=30))
    return {
        "correct": dbResp["correct_picks"],
        "total": dbResp["total_picks"],
    }
