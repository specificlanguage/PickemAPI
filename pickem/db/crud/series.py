from sqlalchemy.orm import Session, aliased
from pickem.db import models, crud


def getSeriesNums():
    # SELECT DISTINCT series_num FROM games ORDER BY series_num
    # It's a hard set value we don't need to query the database.
    return {"seriesNums": [24] + list(range(27, 80))}


def getGamesBySeries(db: Session, seriesNum: int):
    homeTeam = aliased(models.Team, name="ht")
    awayTeam = aliased(models.Team, name="at")
    return crud.games.cleanupGameArraysWithTeams(
        crud.games.getGameBaseQuery(db)
            .where(models.Game.series_num == seriesNum)
        .all())
