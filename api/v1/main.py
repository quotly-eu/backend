from configparser import ConfigParser
from datetime import datetime
import requests
from sqlmodel import select
from __init__ import VERSION, API_NAME
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Routes import
from api.v1.models.models import User
from api.v1.routers import quotes, roles, users
from api.v1.schemas.discord import AccessResponse, UserObject
from database.main import DatabaseHandler

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
    response_model=User
)
def authorize(
  code: str = Query(
    default=...,
    description="The authorization code received from Discord"
  ),
):
  parser = ConfigParser()
  parser.read("config.ini")
  redirect_uri = parser.get("Discord", "redirect_uri")
  client_id = parser.get("Discord", "client_id")
  client_secret = parser.get("Discord", "client_secret")

  access_response = _receive_access_response(code, redirect_uri, client_id, client_secret)
  if not "access_token" in access_response:
    raise HTTPException(status_code=400, detail="Invalid authorization code")
  
  user_info = _receive_user_information(access_response["access_token"])
  if not "id" in user_info:
    raise HTTPException(status_code=400, detail="Invalid user information")

  user = User(
    discord_id=user_info["id"],
    email_address=user_info["email"],
    display_name=user_info["global_name"],
    avatar_url=user_info["avatar"],
    created_at=datetime.now()
  )

  # Check if user exists and if not, add it
  db = DatabaseHandler()

  result = db.session.exec(select(User).where(User.discord_id == user.discord_id)).first()
  if not result:
    db.session.add(user)
    db.session.commit()
  
  return user

def _receive_access_response(
  code: str, 
  redirect_uri: str, 
  client_id: str, 
  client_secret: str
) -> AccessResponse:
  data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": redirect_uri,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  response = requests.post(
    f"{DISCORD_API_ENDPOINT}/oauth2/token",
    data=data,
    headers=headers,
    auth=(client_id, client_secret)
  )
  return response.json()

def _receive_user_information(access_token: str) -> UserObject:
  headers = {"Authorization": f"Bearer {access_token}"}
  response = requests.get(
    f"{DISCORD_API_ENDPOINT}/users/@me",
    headers=headers
  )
  return response.json()

# Include routers
router.include_router(quotes.router)
router.include_router(users.router)
router.include_router(roles.router)
app.include_router(router)