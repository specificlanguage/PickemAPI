from sqlalchemy import update, text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from pickem.db import models, schemas


def setUserPreferences(db: Session, preferences: schemas.UserPreferences):
    """ Update or create a user's preferences. """
    if preferences.favoriteTeam == 0:  # Reset if no team
        preferences.favoriteTeam = None
    userPrefs = models.User(id=preferences.id,
                            favoriteTeam_id=preferences.favoriteTeam,
                            selectionTiming=preferences.selectionTiming,
                            description=preferences.description)
    stmt = insert(models.User).values(userPrefs)
    stmt = stmt.on_conflict_do_update(
        index_elements=[models.User.id],
        set_={
            "favoriteTeam_id": userPrefs.favoriteTeam_id,
            "selectionTiming": userPrefs.selectionTiming,
            "description": userPrefs.description
        }
    )
    db.commit()


def getUserPreferences(db: Session, userID: str):
    """ Get a user's preferences. """
    return db.query(models.User).filter(models.User.id == userID).first()

def getMultipleUsersPreferences(db: Session, userIDs: list[str]):
    return db.query(models.User).filter(models.User.id._in(userIDs)).all()