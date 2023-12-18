# NOTE: this script may not work. If this happens, run the SQL query on the console directly.

from sqlalchemy import text
from db.alchemy import SessionLocal
from db import models

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

with next(get_session()) as session:
    # This works, since all series are supposed to end on Sunday.
    query = session.execute(text(
        """WITH GameSeries AS (
        SELECT
            id,
            date,
            "homeTeam_id",
            "awayTeam_id",
            CASE -- Weekends are automatically OK, just increase by 1 for series
                WHEN extract(DOW FROM date) IN (0, 5, 6) THEN extract(WEEK FROM date) * 2 + 1
                WHEN extract(DOW FROM date) IN (4) THEN
                    CASE -- Special Thursday edition, if it's attached to weekend, then add one, else no.
                        WHEN LAG(date) OVER (PARTITION BY "homeTeam_id",
                            "awayTeam_id" ORDER BY date) IS NULL THEN extract(WEEK FROM date) * 2 + 1
                        ELSE extract(WEEK FROM date) * 2
                        END
                -- Normal weekday series things.
                ELSE extract(WEEK FROM date) * 2 END as series_num
        FROM
            games
        ORDER BY
            date,
                series_num)
        
        UPDATE games
        SET series_num = GameSeries.series_num
        FROM GameSeries
        WHERE GameSeries.id = games.id
    """))
    session.commit()