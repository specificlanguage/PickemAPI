import random, datetime
from typing import Optional

from sqlalchemy import values, insert
from sqlalchemy.orm import Session

from pickem.db.schemas import Game
from pickem.db import models


def getSession(db: Session, uid: str, date: datetime.date, is_series: bool) -> models.Session | None:
    """ Returns the session for a given user on a given date """
    sess = db.query(models.Session).filter(models.Session.date == date, models.Session.user_id == uid, models.Session.is_series == is_series).first()
    if not sess:
        return None
    games = sess.games
    picks = sess.picks
    return sess


def createSession(db: Session, uid: str, game_options: list[Game], is_series: bool, favTeam: Optional[int]) -> models.Session:
    """ Creates a unique session for a user on a given date, optionally with a favorite team. """

    session_games = []
    options = game_options.copy()

    # Extract marquee game already established
    for game in game_options:
        if game.is_marquee:
            session_games.append(game)
            options.remove(game)
        elif favTeam and favTeam == game.homeTeam_id or favTeam == game.awayTeam_id:
            session_games.append(game)
            options.remove(game)

    if len(session_games) == 2: # Both marquee and favTeam games are present
        for _ in range(2):
            session_games.append(random.choice(options))
            options.remove(session_games[-1])
    else:  # Only marquee exists, fill rest
        for _ in range(3):
            session_games.append(random.choice(options))
            options.remove(session_games[-1])

    # Add session information to Session table
    sess = models.Session(date=game_options[0].date, user_id=uid, is_series=is_series)
    for game in session_games:
        sess.games.append(game)
    db.add(sess)  # Games are already added, so no need to do an add_all.
    db.commit()
    db.refresh(sess)
    games = sess.games
    picks = sess.picks
    return sess
