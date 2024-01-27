from typing import Optional

from pydantic import BaseModel
from datetime import date, datetime

class UserPreferences(BaseModel):
    uid: str
    favoriteTeam: int
    selectionTiming: str

class PickBase(BaseModel):
    id: int
    pickedHome: bool

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