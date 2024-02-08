import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from pickem.db import models


def getPicksByUserDate(db: Session, userID: str, year: int, month: int, day: int):
    return (db.query(models.Pick.game_id, models.Pick.pickedHome, models.Game.date, models.Game.id, models.Game.homeTeam, models.Game.awayTeam)
            .join(models.Game, onclause=models.Game.id == models.Pick.game_id)
            .filter(models.Pick.user_id == userID)
            .filter(models.Game.date == datetime.date(year, month, day))
            .all())


def getPicksByUser(db: Session, userID: str):
    return db.query(models.Pick).join(models.Pick.user_id == userID).all()


def getTotalPicksForGame(db: Session, gameID: int):
    """
    Gets the total number of picks, and the number of home picks and away picks for a certain game.
    TODO: next commit: Check to see if game is series instead
    :param db: Database session
    :param gameID: Game ID of the game to get picks for.
    :return: Object containing gameID, total picks, home picks, and away picks.
    """
    subquery = (db.query(func.count("*"))
                .where(models.Pick.game_id == gameID and models.Pick.pickedHome)
                .scalar_subquery())
    return (db.query(
                func.count("*").label("total"),
                subquery.label("home_picks"),
                (func.count("*") - subquery).label("away_picks"))
            .where(models.Pick.game_id == gameID).first())


def get_pick(db: Session, userID: str, gameID: int):
    """
    Gets the pick for a certain game for a certain user.
    :param db: Database session to query
    :param userID: User ID of the pick user.
    :param gameID: Game ID of the game picked.
    :return: The pick object.
    """
    return db.query(models.Pick).filter(models.Pick.user_id == userID and models.Pick.game_id == gameID).first()


def create_pick(db: Session, userID: str, gameID: int, pickedHome: bool, isSeries: bool, comment: str = ""):
    """
    Creates the prediction of a winner for a certain game, known as a pick. Does not check if the pick already exists!
    :param db: Database session to insert into
    :param userID: User ID of the pick user.
    :param gameID: Game ID of the game picked.
    :param pickedHome: Whether the user picked the home team or not. Useful to use this to store less data.
    :param isSeries: Whether the user is picking for the series as a whole, or not
    :param comment: The extra comment the user stores when making this pick.
    :return: The pick object.
    """
    game = db.query(models.Game).filter(models.Game.id == gameID).first()
    gameDate = game.date

    pick = models.Pick(
        user_id=userID,
        game_id=gameID,  # Field is not strictly necessary, but adding for readability's sake.
        pickedHome=pickedHome,
        is_series=isSeries,
        comment=comment
    )

    # Add pick to a session if necessary
    sess = db.query(models.Session).filter(models.Session.user_id == userID and models.Session.date == gameDate).first()

    if sess:
        sess.picks.append(pick)

    db.commit()
    db.refresh(pick)

    return pick


def update_pick(db: Session, userID: str, gameID: int, pickedHome: bool, isSeries: bool, comment: str = ""):
    """
    Updates the pick for a certain game for a certain user. This does not check if a pick already exists!
    :param db: Database session to update into
    :param userID: User ID of the pick user.
    :param gameID: Game ID of the game picked.
    :param pickedHome: Whether the user picked the home team or not. Useful to use this instead of storing homeID, less data.
    :param isSeries: Whether the user is picking for the series as a whole, or not
    :param comment: The extra comment the user stores when making this pick.
    :return: The pick object.
    """
    pick = db.query(models.Pick).filter(models.Pick.user_id == userID and models.Pick.game_id == gameID).first()
    pick.pickedHome = pickedHome
    pick.is_series = isSeries
    pick.comment = comment
    db.commit()
    db.refresh(pick)
    return pick