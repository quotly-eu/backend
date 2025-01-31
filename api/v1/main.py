import sqlmodel
from __init__ import VERSION, API_NAME
from fastapi import APIRouter, FastAPI

# Routes import
from api.v1.models.users import User
from api.v1.routers import quotes, users
from database.main import DatabaseHandler

# FastAPI instance
tags_metadata = [
  {
    "name": "Quotes",
    "description": "Endpoints related to quotes"
  },
  {
    "name": "Users",
    "description": "Endpoints related to quotes"
  }
]

app = FastAPI(
  title=API_NAME,
  version=VERSION,
  openapi_tags=tags_metadata
)
router = APIRouter(prefix="/v1")

# Root endpoints
@router.get("/")
def root():
  """
  This is the root path of the API
  """
  db = DatabaseHandler()
  result = db.session.exec(sqlmodel.select(User)).all()
  return result

# Include routers
router.include_router(quotes.router)
router.include_router(users.router)
app.include_router(router)