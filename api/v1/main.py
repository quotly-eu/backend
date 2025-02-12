from __init__ import VERSION, API_NAME
from configparser import ConfigParser
from datetime import datetime
import jwt
from sqlmodel import select
from fastapi import APIRouter, FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Routes import
from api.v1.models.models import User
from api.v1.routers import quotes, roles, users
from database.main import DatabaseHandler
from discord.main import DiscordOAuthHandler

DISCORD_API_ENDPOINT = "https://discord.com/api/v10"

# FastAPI instance
tags_metadata = [
  {
    "name": "Quotes",
    "description": "Endpoints related to quotes"
  },
  {
    "name": "Users",
    "description": "Endpoints related to users"
  },
  {
    "name": "Roles",
    "description": "Endpoints related to roles"
  }
]

app = FastAPI(
  title=API_NAME,
  version=VERSION,
  openapi_tags=tags_metadata
)
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
):
  """
  Authorize user with Discord

  :return: JWT token
  """
  parser = ConfigParser()
  parser.read("config.ini")
  key = parser.get("JWT", "key")

  dc_handler = DiscordOAuthHandler()

  access_response = dc_handler.receive_access_response(code)
  if not "access_token" in access_response:
    raise HTTPException(status_code=400, detail="Invalid authorization code")
  
  user_info = dc_handler.receive_user_information(access_response["access_token"])
  if not "id" in user_info:
    raise HTTPException(status_code=400, detail="Invalid user information")

  user = User(
    discord_id=user_info["id"],
    email_address=user_info["email"],
    display_name=user_info["global_name"],
    avatar_url=user_info["avatar"],
  )

  # Check if user exists and if not, add it
  db = DatabaseHandler()

  result = db.session.exec(select(User).where(User.discord_id == user.discord_id)).first()
  if not result:
    db.session.add(user)
    db.session.commit()
  
  return jwt.encode(access_response, key)

# Include routers
router.include_router(quotes.router)
router.include_router(users.router)
router.include_router(roles.router)
app.include_router(router)