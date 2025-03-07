from datetime import datetime

import jwt
from fastapi import HTTPException
from sqlmodel import Session, select

from api.v1.models.models import User
from config.main import parser
from discord.main import DiscordOAuthHandler

dc_handler = DiscordOAuthHandler()


def _authorize(
    code: str,
    session: Session,
):
    """
    Authorize user with Discord

    :return: JWT token
    """
    key = parser.get("JWT", "key")

    access_response = dc_handler.receive_access_response(code)
    if not "access_token" in access_response:
        raise HTTPException(status_code=400, detail="Invalid authorization code")

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    if not "id" in user_info:
        raise HTTPException(status_code=400, detail="Invalid user information")

    # Add or update user
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        user = User(
            discord_id=user_info["id"],
            email_address=user_info["email"],
            display_name=user_info["global_name"],
            avatar_url=user_info["avatar"],
            created_at=datetime.now()
        )
    else:
        user.avatar_url = user_info["avatar"]
        user.display_name = user_info["global_name"]
        user.email_address = user_info["email"]

    session.add(user)
    session.commit()

    return jwt.encode(access_response, key)
