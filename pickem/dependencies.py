import logging

from fastapi import HTTPException
from fastapi.requests import Request
from firebase_admin import auth, credentials

from pickem.db.alchemy import SessionLocal

cred = credentials.Certificate("../firebase_acct_key.json")

def get_firebase_user(request: Request):
    id_token = request.headers.get('Authorization')
    if not id_token:
        raise HTTPException(status_code=401, detail="Token id not provided")
    try:
        claims = auth.verify_id_token(id_token)
        return claims["uid"]
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=401, detail="Token id is invalid")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
