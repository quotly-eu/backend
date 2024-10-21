from __init__ import VERSION, API_NAME
from fastapi import APIRouter, FastAPI

# Routes import
from api.v1.routers import quotes

# FastAPI instance
tags_metadata = [
  {
    "name": "Quotes",
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
  return {"message": "Hello World"}

# Include routers
router.include_router(quotes.router)
app.include_router(router)