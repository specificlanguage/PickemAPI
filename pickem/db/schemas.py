from typing import Optional

from pydantic import BaseModel
from datetime import date, datetime

class Date(BaseModel):
    year: int
    month: int
    day: int


class UserPreferences(BaseModel):
    id: str
    favoriteTeam: int
    selectionTiming: str

class PickBase(BaseModel):
    id: int
    pickedHome: bool
    is_series: bool
    comment: str | None = None

class PickCreate(PickBase):
    pass

class Pick(PickBase):
    game_id: int
    class Config:
        from_attributes = True

class GameBase(BaseModel):
    id: int
    finished: bool
    date: date
    startTimeUTC: datetime
    venue: str
    homeTeam_id: int
    awayTeam_id: int

class GameCreate(GameBase):

    class Config:
        from_attributes = True

class Game(GameBase):
    pass

class TeamBase(BaseModel):
    id: int
    name: str
    cityName: str
    teamName: str
    logo: str
    abbr: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    homeGames: list[Game] = []
    awayGames: list[Game] = []

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    id: int
    date: date
    user_id: str
    games: list[Game]
    picks: list[Pick]
    isSeries: bool