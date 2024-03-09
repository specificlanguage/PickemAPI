import logging
import os
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from pickem.dependencies import get_db, get_user, get_user_optional
from pickem.db.crud.users import getUserPreferences, setUserPreferences
from pickem.db import schemas

router = APIRouter(
    prefix="/users",
    tags=["users"],
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
    if (userID == uid):
        return res
    else:
        return {
            "id": uid,
            "favoriteTeam_id": res.favoriteTeam_id
        }

@router.get("/all")
@cache(expire=60 * 60 * 24)
async def getUsers():
    clerkResp = httpx.get(
        "https://api.clerk.dev/v1/users",
        headers={"Authorization": "Bearer " + os.environ["CLERK_API_KEY"]}).json()
    print(clerkResp)
    users = {user["id"]: {"id": user["id"], "username": user["username"]} for user in clerkResp}
    return {
        "users": users
    }