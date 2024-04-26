import logging

from sqlalchemy import select, insert, text, func
from sqlalchemy.orm import Session
from pickem.db import models, schemas
from datetime import datetime
import httpx

from pickem.db.alchemy import SessionLocal

SEASON = 2024
AL_ID, NL_ID = 103, 104

session = SessionLocal()


def create_team(db: Session, team: schemas.TeamCreate):
    db_team = models.Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)


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


def setupTeams(db: Session):
    """ Sets up all teams in the database. Replaces load_teams.py from scripts. """
    with httpx.Client() as client:
        # American League first
        r = client.get(
            "https://statsapi.mlb.com/api/v1/teams?season={0}&leagueIds={1},{2}".format(SEASON, AL_ID, NL_ID))
        resp = r.json()
        for team in resp['teams']:
            teamObj = schemas.TeamCreate(
                id=team["id"],
                name=team["name"],
                cityName=team["locationName"],
                teamName=team["teamName"],
                logo="",
                abbr=team["abbreviation"]
            )
            print("creating {0} ({1})".format(teamObj.name, teamObj.id))
            create_team(session, teamObj)


def calc_series(db: Session):
    """ Calculates the series that each game belongs to.
        Each series is a set of games between two teams, and always has games ending on Sunday.
        Thursdays can go either way, so we need to check if it's attached to a weekend or not.
        This script is a replacement for calc_series.py.
    """
    session.execute(text(
        """WITH GameSeries AS (
        SELECT
            id,
            date,
            "homeTeam_id",
            "awayTeam_id",
            CASE -- Weekends are automatically OK, just increase by 1 for series
                WHEN extract(DOW FROM date) IN (0, 5, 6) THEN extract(WEEK FROM date) * 2 + 1
                WHEN extract(DOW FROM date) IN (4) THEN
                    CASE -- Special Thursday edition, if it's attached to weekend, then add one, else no.
                        WHEN LAG(date) OVER (PARTITION BY "homeTeam_id",
                            "awayTeam_id" ORDER BY date) IS NULL THEN extract(WEEK FROM date) * 2 + 1
                        ELSE extract(WEEK FROM date) * 2
                        END
                -- Normal weekday series things.
                ELSE extract(WEEK FROM date) * 2 END as series_num
        FROM
            games
        ORDER BY
            date,
                series_num)
        
        UPDATE games
        SET series_num = GameSeries.series_num
        FROM GameSeries
        WHERE GameSeries.id = games.id
    """))
    session.commit()


def main():
    """ Main function to load all teams and games into the database."""

    # Get all teams from the database.
    teams = session.scalars(select(models.Team)).all()

    # If teams not set up, then set them up.
    if len(teams) == 0:
        logging.info("Teams not yet loaded into the database, creating teams.")
        setupTeams(session)

    # If games are already uploaded, then disregard this script entirely.
    num_games = session.scalars(func.count(models.Game.id)).first()
    if num_games == 2430:  # 30 teams * 81 home games
        logging.info("Games already loaded into the database, skipping script.")
        exit(0)

    # Query the MLB API for all games for each team.
    with (httpx.Client() as client):
        for team in teams:
            logging.info("Loading games for", team.teamName)
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
            logging.info("Processing {0} games for {1}".format(len(games), team.teamName))
            create_games(session, list(games.values()))

    # Generate series numbers for all games.
    calc_series(session)

    # Generate the marquee games.
    session.execute(text("""
            UPDATE games SET is_marquee = CASE
                WHEN id IN (
                SELECT DISTINCT ON (date) id FROM games ORDER BY date, random()
                ) THEN True ELSE False END;
        """))
    session.commit()


main()
