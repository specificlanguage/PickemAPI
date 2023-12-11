from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .alchemy import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    logo = Column(String)
    games = relationship("Game")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    homeTeam_id = Column(Integer, ForeignKey("teams.id"))
    awayTeam_id = Column(Integer, ForeignKey("teams.id"))
    finished = Column(Boolean)
    picks = relationship("Pick", back_populates="game")

class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    game_id = Column(Integer, ForeignKey("games.id"))
    pickedHome = Column(Boolean)
    game = relationship("Game", back_populates="picks")


