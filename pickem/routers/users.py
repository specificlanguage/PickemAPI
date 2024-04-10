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
from pickem.lib.users import getUsersFromClerk

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


@router.put("/preferences")
def set_preferences(favoriteTeam: Annotated[int | None, Body()],
                    selectionTiming: Annotated[str, Body()],
                    description: Annotated[str | None, Body()],
                    userID: str = Depends(get_user),
                    db: Session = Depends(get_db)):
    setUserPreferences(db, schemas.UserPreferences(
        favoriteTeam=favoriteTeam,
        selectionTiming=selectionTiming,
        description=description,
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
            "favoriteTeam_id": res.favoriteTeam_id,
            "description": res.description,
        }


@router.get("/all")
@cache(expire=60 * 60 * 24)
async def getUsers():
    clerkResp = getUsersFromClerk()
    users = {user["id"]: {"id": user["id"], "username": user["username"], "image_url": user["image_url"]} for user in
             clerkResp}
    return {
        "users": users
    }


@router.get("/{user_identifier}")
async def getUserByID(user_identifier: str, db: Session = Depends(get_db)):
    """ Retrieves a user and their information by their ID or username from Clerk."""
    users = getUsersFromClerk()
    user = next((user for user in users if user["id"] == user_identifier or user["username"] == user_identifier), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    uid = user["id"]

    res = getUserPreferences(db, uid)
    if not res:
        raise HTTPException(status_code=404, detail="User does not exist in database, generate this in settings")
    return {
        "id": user["id"],
        "username": user["username"],
        "image_url": user["image_url"],
        "favoriteTeam_id": res.favoriteTeam_id,
        "description": res.description
    }

