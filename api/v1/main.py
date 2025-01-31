import sqlmodel
from __init__ import VERSION, API_NAME
from fastapi import APIRouter, FastAPI

# Routes import
from api.v1.routers import quotes, roles, users

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
router = APIRouter(prefix="/v1")

# Include routers
router.include_router(quotes.router)
router.include_router(users.router)
router.include_router(roles.router)
app.include_router(router)