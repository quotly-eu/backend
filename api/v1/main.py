from configparser import ConfigParser
from datetime import datetime

import jwt
from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from __init__ import VERSION, API_NAME
from api.v1.models.models import User
from api.v1.routers import quotes, roles, users
from config.main import tags_metadata, parser
from database.main import DatabaseHandler
from discord.main import DiscordOAuthHandler

app = FastAPI(
    title=API_NAME,
    version=VERSION,
    openapi_tags=tags_metadata
)
db = DatabaseHandler()
dc_handler = DiscordOAuthHandler()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/v1")


# Root endpoints
@router.post(
    "/authorize",
    response_model=str,
)
def authorize(
    code: str = Form(..., description="Authorization code received from Discord", example="1234567890"),
    session: Session = Depends(db.get_session),
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


# Include routers
router.include_router(quotes.router)
router.include_router(users.router)
router.include_router(roles.router)
app.include_router(router)
