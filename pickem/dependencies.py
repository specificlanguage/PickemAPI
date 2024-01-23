import logging

from fastapi import HTTPException
from fastapi.requests import Request

from pickem.db.alchemy import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
