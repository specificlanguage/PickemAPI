"""
This module contains functions that provide status updates for games in real time.
See the live stats repo (https://github.com/specificlanguage/PickemGoLiveStats) for more information.
"""
from redis import Redis


async def retrieveStats(gameID: int, cache: Redis):
    """
    Retrieves the stats for a game with the given ID.
    """
    response = cache.hgetall("game:" + str(gameID))
    if not response:
        return {"error": "Game does not have live stats."}
    for key in response:
        if response[key].isnumeric():
            response[key] = int(response[key])
    return response

