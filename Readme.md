## Pick'em API

This is the associated backend API for the Pickem project that I'm working on, which allows users to predict games. This is not a betting site.

### Setting Up

- Setup your `.env` with a Postgres database (I'm using [neon.tech](https://neon.tech)) and a secret key from [Clerk](https://clerk.com) which is being used for authentication on the frontend.
- Run `alembic upgrade head` to create tables and format the database.
- Run `load_teams.py, load_games.py` to create information about the teams. If you're reading this past 2024, you may need to change this.
- Boot up your FastAPI located in main.py.