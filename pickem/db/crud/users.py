from sqlalchemy import update, text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from pickem.db import models, schemas


def setUserPreferences(db: Session, preferences: schemas.UserPreferences):
    """ Update or create a user's preferences. """
    userPrefs = models.User(id=preferences.id,
                            favoriteTeam_id=preferences.favoriteTeam if preferences.favoriteTeam else None,
                            selectionTiming=preferences.selectionTiming if preferences.selectionTiming else None,
                            description=preferences.description)
    if preferences.favoriteTeam == 0:  # Reset if no team
        userPrefs.favoriteTeam_id = None
    stmt = insert(models.User).values(
        id=userPrefs.id,
        favoriteTeam_id=userPrefs.favoriteTeam_id,
        selectionTiming=userPrefs.selectionTiming,
        description=userPrefs.description
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "favoriteTeam_id": userPrefs.favoriteTeam_id,
            "selectionTiming": userPrefs.selectionTiming,
            "description": userPrefs.description
        }
    )
    db.execute(stmt)
    db.refresh(userPrefs)
    db.commit()


def getUserPreferences(db: Session, userID: str) -> models.User:
    """ Get a user's preferences. """
    return db.query(models.User).filter(models.User.id == userID).first()

def getMultipleUsersPreferences(db: Session, userIDs: list[str]):
    return db.query(models.User).filter(models.User.id._in(userIDs)).all()