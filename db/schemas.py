from pydantic import BaseModel

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

class GameCreate(GameBase):
    homeTeam_id: int
    awayTeam_id: int
    picks: list[Pick] = []

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