from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from db import crud, series
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)


@router.get("/teams")
async def get_games_with_teams(team1_abbr: str | None = None,
                               team2_abbr: str | None = None,
                               team1_id: int | None = None,
                               team2_id: int | None = None,
                               db: Session = Depends(get_db)):
    if team1_id is None or team2_id is None:
        if team1_abbr is None or team2_abbr is None:
            raise HTTPException(status_code=400, detail=
            "Either team1_id/team2_id must be specified, or team1_abbr/team2_abbr.")
        games = crud.getGamesWithAbbr(db, team1_abbr, team2_abbr)
        return games

    return crud.getGamesWithTeams(db, team1_id, team2_id)


@router.get("/date")
async def get_game_by_date(year: int, month: int, day: int, db: Session = Depends(get_db)):
    return crud.getGameByDate(db, year, month, day)


@router.get("/series/seriesNums")
async def get_series_nums():
    return series.getSeriesNums()


@router.get("/series")
async def get_game_by_series(seriesNum: int, db: Session = Depends(get_db)):
    games = series.getGamesBySeries(db, seriesNum)
    if len(games) == 0:
        raise HTTPException(status_code=404, detail="No games for this series number")
    return games


@router.get("/{id}")
async def get_game(id: str, db: Session = Depends(get_db)):
    game = crud.getGame(db, int(id))
    if not game:
        raise HTTPException(status_code=404, detail="Game does not exist")
    return game