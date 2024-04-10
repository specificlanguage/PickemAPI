from sqlalchemy import update, text
from sqlalchemy.orm import Session

from pickem.db import models, schemas


def setUserPreferences(db: Session, preferences: schemas.UserPreferences):
    """ Update or create a user's preferences. """
    if preferences.favoriteTeam == 0:  # Reset if no team
        preferences.favoriteTeam = None
    userPrefs = models.User(id=preferences.id,
                            favoriteTeam_id=preferences.favoriteTeam,
                            selectionTiming=preferences.selectionTiming,
                            description=preferences.description)
    db.execute(text(f"""
        INSERT INTO users ("id", "favoriteTeam_id", "selectionTiming") 
        VALUES ('{userPrefs.id}', {userPrefs.favoriteTeam_id or 'NULL'}, '{userPrefs.selectionTiming}') 
        ON CONFLICT (id) DO UPDATE SET
        "favoriteTeam_id" = {userPrefs.favoriteTeam_id or 'NULL'},
        "selectionTiming" = '{userPrefs.selectionTiming}'
        "description" = '{userPrefs.description}'
    """))
    db.commit()


def getUserPreferences(db: Session, userID: str):
    """ Get a user's preferences. """
    return db.query(models.User).filter(models.User.id == userID).first()

def getMultipleUsersPreferences(db: Session, userIDs: list[str]):
    return db.query(models.User).filter(models.User.id._in(userIDs)).all()