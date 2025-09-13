from fastapi import APIRouter, Depends, FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from __init__ import VERSION, API_NAME
from api.v1.routers import quotes, roles, users
from api.v1.schemas.discord import AuthorizeBody
from api.v1.tasks.main import _authorize
from config.main import tags_metadata
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
    allow_credentials=True,
    allow_origins=["*"],
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
    payload: AuthorizeBody,
    session: Session = Depends(db.get_session),
):
    """
    Authorize user with Discord

    :return: JWT token
    """
    return _authorize(payload.code, session)


# Include routers
router.include_router(quotes.router)
router.include_router(users.router)
router.include_router(roles.router)
app.include_router(router)
