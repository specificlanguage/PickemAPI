from sqlalchemy.orm import Session, aliased
from .. import models, schemas

def getUserByUsername(db: Session, username: str):
    """Get a user by their username, or returns None if not found."""
    return db.query(models.User).where(models.User.username == username).first()

def getUserByID(db: Session, id: str):
    """Get a user by their ID, or returns None if not found."""
    return db.query(models.User).where(models.User.id == id).first()

def insertUser(db: Session, username: str, uid: str, email: str, imageURL=None):
    user = models.User(
        username=username,
        uid=uid,
        email=email,
        imageURL=imageURL)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user