from typing import Annotated

import httpx
import os

from fastapi import HTTPException, Header
from jwt import JWT, jwk_from_dict

from pickem.db.alchemy import SessionLocal

JWT_Instance = JWT()
AUTHORIZED_PARTIES = ["http://localhost:5173"]


def get_user(authorization: Annotated[str | None, Header()] = None):
    """ Decodes an authentication token in the request header and returns the user ID. """

    # Query the Clerk API to get JWKS, get token and signing key
    resp = httpx.get("https://api.clerk.dev/v1/jwks",
                     headers={"Authorization": "Bearer " + os.environ["CLERK_API_KEY"]}).json()
    signing_key = jwk_from_dict(resp["keys"][0])
    token = authorization.split(" ")[1]

    # Verify token, expiration time, and authorized party
    message_received = JWT_Instance.decode(token, signing_key)
    if message_received.get("azp") not in AUTHORIZED_PARTIES:
        raise HTTPException(401, detail="Internal service error")
    return message_received.get("sub")

def get_user_optional(authorization: Annotated[str | None, Header()] = None):
    """ Provides optional authentication for endpoints that don't always require it."""
    try:
        return get_user(authorization)
    except:
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
