import random, datetime
from typing import Optional

from sqlalchemy import values, insert
from sqlalchemy.orm import Session

from pickem.db.schemas import Game
from pickem.db import models


def getSession(db: Session, uid: str, date: datetime.date) -> models.Session | None:
    """ Returns the session for a given user on a given date """
    sess = db.query(models.Session).filter(models.Session.date == date, models.Session.user_id == uid).first()
    if not sess:
        return None
    games = sess.games
    picks = sess.picks
    return sess


def createSession(db: Session, uid: str, game_options: list[Game], selTiming: str, favTeam: Optional[int]) -> models.Session:
    """ Creates a unique session for a user on a given date, optionally with a favorite team. """

    # Add session information to Session table
    sess = models.Session(date=game_options[0].date, user_id=uid, is_series=(selTiming == "series"))
    for game in generateSessionGames(game_options, selTiming, favTeam):
        sess.games.append(game)
    db.add(sess)  # Games are already added, so no need to do an add_all.
    db.commit()
    db.refresh(sess)
    games = sess.games
    picks = sess.picks
    return sess


def generateSessionGames(game_options: list[Game], selTiming: str, favTeam: Optional[int]):
    """ Generates a list of games for a session based on the game options and user preferences. """
    session_games = []
    options = game_options.copy()

    marqueeGame = None
    favTeamGame = None

    for game in game_options:
        if game.is_marquee:
            marqueeGame = game
            options.remove(game)
        elif favTeam and favTeam == game.homeTeam_id or favTeam == game.awayTeam_id:
            favTeamGame = game
            options.remove(game)

    if selTiming == "series":
        # TODO - Implement logic for series.
        # This shouldn't be extremely hard, but date check logic is mostly the issue here.
        pass
    if selTiming == "daily":
        if favTeamGame: session_games.append(favTeamGame)
        if marqueeGame: session_games.append(marqueeGame)
        while len(session_games) < 4 and options:
            session_games.append(random.choice(options))
            options.remove(session_games[-1])
    if selTiming == "singleteam":
        if favTeamGame: session_games.append(favTeamGame)
        else: session_games.append(marqueeGame) # Fall back to marquee game if no favorite team game
    if selTiming == "marquee":
        session_games.append(marqueeGame)
        if favTeamGame: session_games.append(favTeamGame)
        while len(session_games) < 2 and options:
            session_games.append(random.choice(options))
            options.remove(session_games[-1])
    return session_games
