from pydantic import BaseModel

class TeamBase(BaseModel):
    id: int
    name: str
    logo: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    owner_id: int

    class Config:
        orm_mode = True

class PickBase(BaseModel):
    id: int
    pickedHome: bool

class PickCreate(PickBase):
    pass

class Pick(PickBase):
    game_id: int
    class Config:
        orm_mode = True

class GameBase(BaseModel):
    id: int
    finished: bool

class GameCreate(GameBase):
    homeTeam_id: int
    awayTeam_id: int
    picks: list[Pick] = []

    class Config:
        orm_mode = True