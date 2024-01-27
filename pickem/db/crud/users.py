from sqlalchemy import update
from sqlalchemy.orm import Session

from pickem.db import models, schemas


def setUserPreferences(db: Session, preferences: schemas.UserPreferences):
    """ Update or create a user's preferences. """
    userPrefs = models.User(id=preferences.id,
                            favoriteTeam_id=preferences.favoriteTeam,
                            selectionTiming=preferences.selectionTiming)
    if (db.query(models.User).filter(models.User.id == userPrefs.id).first()):
        update(models.User).where(models.User.id == userPrefs.id).values(
            {"favoriteTeam_id": userPrefs.favoriteTeam_id,
             "selectionTiming": userPrefs.selectionTiming})
    else:
        db.add(userPrefs)
        db.commit()
        db.refresh(userPrefs)


def getUserPreferences(db: Session, userID: str):
    """ Get a user's preferences. """
    return db.query(models.User).filter(models.User.id == userID).first()
