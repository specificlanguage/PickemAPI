"""
This should only be used as a one-time use script to generate the "marquee" games for each day.
Marquee games are kind of like the "title" games that everyone, regardless of team preference, will pick.
Ideally, these are games that are interesting, but we can set the information for this later.
One game per day will be picked.

We will have a different method for setting the marquee games for each series.
"""

from sqlalchemy import text
from pickem.db.alchemy import SessionLocal

session = SessionLocal()

with session as s:
    s.execute(text("""
        UPDATE games SET is_marquee = CASE 
            WHEN id IN (
            SELECT DISTINCT ON (date) id FROM games ORDER BY date, random()
            ) THEN True ELSE False END;
    """))
    s.commit()