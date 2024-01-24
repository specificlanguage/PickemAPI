from sqlalchemy import select, insert, text
from sqlalchemy.orm import Session
from pickem.db import models, schemas
from datetime import datetime
import httpx

from pickem.db.alchemy import SessionLocal

SEASON = 2024
AL_ID, NL_ID = 103, 104


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_games_for_team_id(db: Session, team_id: int):
    """ Gets all games from the database that match the team_id, either playing home or away.."""
    return db.execute(text("""
        SELECT * FROM games WHERE "homeTeam_id"={0} OR "awayTeam_id"={0};
    """.format(team_id)))


def create_games(db: Session, games: list[dict]):
    if len(games) == 0: return
    """ Batch uploads games into the database."""
    db.execute(
        insert(models.Game),
        games,
    )
    db.commit()


def create_game(db: Session, game: schemas.GameCreate):
    """ Adds the game into the database. """
    db_team = models.Game(**game.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)


def createGameObject(game):
    """ Adds all critical game information into a schema."""
    return {
        "id": game["gamePk"],
        "date": datetime.strptime(game["officialDate"], "%Y-%m-%d"),
        "startTimeUTC": datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ"),
        "venue": game["venue"]["name"],
        "homeTeam_id": game["teams"]["home"]["team"]["id"],
        "awayTeam_id": game["teams"]["away"]["team"]["id"],
        "finished": False,
    }


with next(get_session()) as session:
    statement = select(models.Team)
    teams = session.scalars(select(models.Team)).all()

with (httpx.Client() as client):
    for team in teams:
        print("loading games for", team.teamName)
        games = {}
        # Note: The start date is March 20 due to MLB playing games in Korea on the 20th/21st.
        # Please change and revert these dates as necessary.
        dates = client.get(
            "https://statsapi.mlb.com/api/v1/schedule/?"
            "sportId=1&season={0}&scheduleTypes=games&teamId={1}&"
            "startDate=2024-03-20&endDate=2024-09-29&gameType=R"
            .format(SEASON, team.id)).json()["dates"]
        for dateObj in dates:
            date = dateObj["date"]
            for game in dateObj["games"]:
                gameObj = createGameObject(game)
                games[gameObj["id"]] = gameObj

        games_inserted = get_games_for_team_id(session, team.id)
        for game in games_inserted:  # Remove games that already exist in the database.
            if game.id in games:
                print(game.id, games[game.id])
                del games[game.id]
        print("processing {0} games for {1}".format(len(games), team.teamName))
        create_games(session, list(games.values()))
