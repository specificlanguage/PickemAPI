from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pickem.dependencies import get_db, get_firebase_user
from pickem.db.crud import users
from pickem.db.schemas import UserBase

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


@router.get("/")
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = users.getUserByUsername(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user


@router.get("/")
async def get_user_by_id(id: str, db: Session = Depends(get_db)):
    user = users.getUserByID(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user


@router.post("/")
async def createUser(user: UserBase, db: Session = Depends(get_db)):
    if users.getUserByUsername(db, user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    user = users.insertUser(db, user.username, user.uid, user.email, user.imageURL)
    return user

@router.delete("/")
async def deleteUser(user=Depends(get_firebase_user), db: Session = Depends(get_db)):
    if (user.uid):
        raise HTTPException(status_code=404, detail="Unauthorized")
    users.deleteUser(db, id)
    return {"message": "User deleted"}