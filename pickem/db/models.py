from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Text, Table
from sqlalchemy.orm import relationship
from .alchemy import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, unique=True)
    favoriteTeam_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    favoriteTeam = relationship("Team", foreign_keys=[favoriteTeam_id])
    selectionTiming = Column(String, nullable=False)


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
    is_marquee = Column(Boolean)
    series_num = Column(Integer)

class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    pickedHome = Column(Boolean)
    game = relationship("Game", back_populates="picks")
    comment = Column(Text)

""" Many-to-many association tables for session games."""
sessionToGames = Table(
    "session_games",
    Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id")),
    Column("session_id", Integer, ForeignKey("sessions.id")),
)

sessionToPicks = Table(
    "session_picks",
    Base.metadata,
    Column("pick_id", Integer, ForeignKey("picks.id")),
    Column("session_id", Integer, ForeignKey("sessions.id")),
)

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    date = Column(Date)
    is_series = Column(Boolean)
    games = relationship("Game", secondary=sessionToGames, back_populates="sessions")
    picks = relationship("Pick", secondary=sessionToPicks, back_populates="sessions")
