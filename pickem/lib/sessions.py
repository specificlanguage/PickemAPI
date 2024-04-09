from datetime import date
from pydantic import BaseModel
from pickem.db.schemas import Game


class Session(BaseModel):
    id: int
    user_id: str
    date: date
    games: list[Game]


