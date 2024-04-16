import datetime
from sqlalchemy import func, text, case
from sqlalchemy.orm import Session
from pickem.db import models
from pickem.db.schemas import PickCreate


def getPicksByUserDate(db: Session, userID: str, year: int, month: int, day: int, isSeries: bool):
    """
    Gets the picks for a certain user on a certain date.
    :param db: Database session instance
    :param userID: User id
    :param year: Year
    :param month: Month
    :param day: Day
    :return:
    """
    return (db.query(models.Pick.game_id, models.Pick.pickedHome, models.Pick.is_series, models.Pick.comment)
            .join(models.Game, onclause=models.Game.id == models.Pick.game_id)
            .filter(models.Pick.user_id == userID)
            .filter(models.Pick.is_series == isSeries)
            .filter(models.Game.date == datetime.date(year, month, day))
            .all())


def getUserPickHistory(db: Session, userID: str, offset: int = 0, limit: int = 100):
    """
    Retrieves a user's pick history, and also populates the games within this list.
    :param db: Database session
    :param userID: User ID
    :param offset: Offset to retrieve
    :param limit: The number of items to retrieve -- set to 100 by default, but can be changed if desired.
    :return:
    """
    queryResult = db.execute(text("""
        SELECT picks.*, games.*,
        games.date as "date",
        picks.id IN (SELECT session_picks.pick_id FROM session_picks) as "inSession"
        FROM picks, games
        WHERE picks.user_id = :userID AND picks.game_id = games.id AND games.date <= CURRENT_DATE
        ORDER BY "startTimeUTC" DESC
        LIMIT :limit OFFSET :offset;
    """), {"userID": userID, "limit": limit, "offset": offset}).mappings().all()


    # print([str(p) for p in picks])
    # # games = [p.game for p in picks]
    return queryResult

def getTotalPicksForGame(db: Session, gameID: int, isSeries: bool):
    """
    Gets the total number of picks, and the number of home picks and away picks for a certain game.
    TODO: next commit: Check to see if game is series instead
    :param db: Database session
    :param gameID: Game ID of the game to get picks for.
    :param isSeries: Whether the picks should be queried by series or not.
    :return: Object containing gameID, total picks, home picks, and away picks.
    """
    subquery = (db.query(func.count("*"))
                .where(models.Pick.game_id == gameID, models.Pick.pickedHome, models.Pick.is_series == isSeries)
                .scalar_subquery())
    return (db.query(
                func.count("*").label("total"),
                subquery.label("home_picks"),
                (func.count("*") - subquery).label("away_picks"))
            .where(models.Pick.game_id == gameID, models.Pick.is_series == isSeries).first())


def get_picks(db: Session, gameIDs: list[int], isSeries: bool, userID: str = None) -> models.Pick:
    """
    Gets the total number of picks, and the number of home picks and away picks for multiple specified games.
    :param db:
    :param gameIDs:
    :param isSeries:
    :return: List of pick objects
    """
    return db.query(models.Pick).filter(models.Pick.game_id.in_(gameIDs), models.Pick.user_id == userID, models.Pick.is_series == isSeries).all()


def get_pick(db: Session, userID: str, gameID: int):
    """
    Gets the pick for a certain game for a certain user.
    :param db: Database session to query
    :param userID: User ID of the pick user.
    :param gameID: Game ID of the game picked.
    :return: The pick object.
    """
    return db.query(models.Pick).filter(models.Pick.user_id == userID, models.Pick.game_id == gameID).first()


def create_picks(db: Session, userID: str, picks: list[PickCreate]):
    """
    Creates a list of picks for a user.
    Same functionality as create_pick, but for multiple picks.
    Note that this function assumes all games picked are the same date and the same type of is_series.
    Writes the picks to the database, updates if already present.
    :param db: Database session
    :param userID: User ID
    :param picks: The picks for the specific database.
    :return:
    """
    gameIDs = [pick.gameID for pick in picks]
    games = db.query(models.Game).filter(models.Game.id.in_(gameIDs)).all()

    # Check which picks already exist in this current instance
    picksExist = db.query(models.Pick).filter(
        models.Pick.game_id.in_(gameIDs),
        models.Pick.user_id == userID).all()
    picksAlreadyExist = {pick.game_id: pick for pick in picksExist}

    # Check if a session exists for this user.
    sess = db.query(models.Session).filter(
        models.Session.user_id == userID,
        models.Session.is_series == picks[0].isSeries,
        models.Session.date == games[0].date).first()

    # Offload anything that already exists in the session
    picksInSess = []
    if sess is not None:
        picksInSess = [pick.game_id for pick in sess.picks]

    pickObjects = [models.Pick(
        user_id=userID,
        game_id=pick.gameID,
        pickedHome=pick.pickedHome,
        is_series=pick.isSeries,
        comment=pick.comment
    ) for pick in picks]

    for pickObject in pickObjects:
        if pickObject.game_id in picksAlreadyExist:  # Update instead of add
            existingPick = picksAlreadyExist[pickObject.game_id]
            existingPick.pickedHome = pickObject.pickedHome
            existingPick.is_series = pickObject.is_series
            existingPick.comment = pickObject.comment
            db.refresh(existingPick)
        elif pickObject.game_id not in picksInSess:  # Add via session if present
            sess.picks.append(pickObject)
        else:
            db.add(pickObject)

    db.commit()

def create_pick(db: Session, userID: str, gameID: int, pickedHome: bool, isSeries: bool, comment: str = ""):
    """
    Creates the prediction of a winner for a certain game, known as a pick. Merges pick if already exists.
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

    # Add pick to a session if necessary -- only if it matches.
    sess = db.query(models.Session).filter(
        models.Session.user_id == userID,
        models.Session.date == gameDate).first()

    if sess:
        games = sess.games
        if game in games:
            sess.picks.append(pick)
        else:
            db.add(pick)
    else:
        db.add(pick)


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
    pick = db.query(models.Pick).filter(models.Pick.user_id == userID, models.Pick.game_id == gameID).first()
    pick.pickedHome = pickedHome
    pick.is_series = isSeries
    pick.comment = comment
    db.commit()
    db.refresh(pick)
    return pick

def get_leaders(db: Session, is_series: bool):
    """
    Get pick leaders for the entire season.
    """
    return (
        db.execute(text("""
            SELECT picks.user_id as "userID",
                   sum(case when picks.correct = true then 1 else 0 end) as "correctPicks",
                   count(picks.user_id) as "totalPicks"
            from picks
            WHERE picks.id in (SELECT pick_id from session_picks) and picks.is_series = :is_series
            GROUP BY picks.user_id
            ORDER BY "correctPicks" DESC;
        """), {"is_series": is_series}).all()
    )