from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from .alchemy import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    cityName = Column(String)
    teamName = Column(String)
    logo = Column(String)
    abbr = Column(String)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    homeTeam_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    awayTeam_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    date = Column(Date)
    startTimeUTC = Column(DateTime)
    venue = Column(String)
    finished = Column(Boolean)
    homeTeam = relationship("Team", foreign_keys=[homeTeam_id])
    awayTeam = relationship("Team", foreign_keys=[awayTeam_id])
    picks = relationship("Pick", back_populates="game")

class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    game_id = Column(Integer, ForeignKey("games.id"))
    pickedHome = Column(Boolean)
    game = relationship("Game", back_populates="picks")


