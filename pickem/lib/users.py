import os
import httpx


def getUsersFromClerk():
    """ Helper function to retrieve users from Clerk. """
    clerkResp = httpx.get(
        "https://api.clerk.dev/v1/users",
        headers={"Authorization": "Bearer " + os.environ["CLERK_API_KEY"]}).json()
    return clerkResp


def getUserIdByUsername(username: str):
    """ Retrieves a user by their username from Clerk. """
    clerkResp = getUsersFromClerk()
    users = filter(lambda user: user["username"] == username, clerkResp)
    try:
        return next(users)["id"]
    except StopIteration:
        return None
