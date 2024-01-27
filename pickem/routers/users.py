import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from pickem.dependencies import get_db, get_user, get_user_optional
from pickem.db.crud.users import getUserPreferences, setUserPreferences
from pickem.db import schemas

router = APIRouter(
    prefix="/users",
    tags=["picks"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)

@router.put("/preferences")
def set_preferences(favoriteTeam: Annotated[int | None, Body()],
                    selectionTiming: Annotated[str, Body()],
                    userID: str = Depends(get_user),
                    db: Session = Depends(get_db)):
    setUserPreferences(db, schemas.UserPreferences(
        favoriteTeam=favoriteTeam,
        selectionTiming=selectionTiming,
        id=userID))
    return {"message": "Preferences updated"}

@router.get("/preferences")
def get_preferences(uid: str,
        userID: str | None = Depends(get_user_optional),
        db: Session = Depends(get_db)):
    res = getUserPreferences(db, uid)
    if(userID == uid):
        return res
    else:
        return {
            "id": uid,
            "favoriteTeam_id": res.favoriteTeam_id
        }