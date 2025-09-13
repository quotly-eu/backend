from typing import Literal, Union

from fastapi import APIRouter, Depends, Form, Query
from sqlmodel import Session

from api.v1.models.models import QuoteComment, QuoteReaction
from api.v1.schemas.discord import TokenBase
from api.v1.schemas.quotes import CreateQuoteBody, CreateQuoteCommentBody, QuoteCommentSchema, QuoteSchema, SavedQuoteSchema, ToggleQuoteReactionBody
from api.v1.tasks.quotes import (
    _get_quotes,
    _create_quote,
    _get_top_quotes,
    _get_quote,
    _delete_quote,
    _is_quote_saved,
    _get_quote_reactions, _get_quote_comments, _create_quote_comment, _quote_toggle_react, _quote_toggle_save
)
from database.main import DatabaseHandler
from discord.main import DiscordOAuthHandler

router = APIRouter(
    prefix="/quotes", tags=["Quotes"]
)

db = DatabaseHandler()
dc_handler = DiscordOAuthHandler()


@router.get(
    "", response_model=list[QuoteSchema]
)
def get_quotes(
    page: int = Query(
        default=None, description="The page number to retrieve starting from 1"
    ),
    limit: int = Query(
        default=None, description="The number of items to retrieve"
    ),
    search: str = Query(
        default=None, description="The search term to filter quotes by",
    ),
    sort: Literal["ascend", "descend"] = Query(
        default="descend", description="The order to sort the quotes by"
    ),
    token: str = Query(
        default=None, description="The JWT token from the current user"
    ),
    session: Session = Depends(db.get_session),
):
    return _get_quotes(page, limit, search, sort, token, session)


@router.post(
    "/create", response_model=QuoteSchema
)
def create_quote(
    payload: CreateQuoteBody,
    session: Session = Depends(db.get_session),
):
    return _create_quote(payload.quote, payload.token, payload.send_webhook, session)


@router.get(
    "/top", response_model=list[QuoteSchema], )
def get_top_quotes(
    limit: int = Query(default=10, description="The number of top quotes to retrieve"),
    token: str = Query(default=None, description="The JWT token from the current user"),
    session: Session = Depends(db.get_session),
):
    # Get top quotes of the last 30 days sorted by QuoteReaction count
    return _get_top_quotes(limit, token, session)


@router.get(
    "/{id}", response_model=QuoteSchema
)
def get_quote(
    id: int,
    token: str = Query(
        default=None, description="The JWT token from the current user"
    ),
    session: Session = Depends(db.get_session),
):
    return _get_quote(id, token, session)


@router.delete(
    "/{id}/delete", response_model=None
)
def delete_quote(
    id: int,
    payload: TokenBase,
    session: Session = Depends(db.get_session)
):
    return _delete_quote(id, payload.token, session)


@router.get(
    "/{id}/saved", response_model=Union[SavedQuoteSchema, None]
)
def is_quote_saved(
    id: int,
    token: str = Query(..., description="The JWT token from the current user"),
    session: Session = Depends(db.get_session)
):
    return _is_quote_saved(id, token, session)


@router.get(
    "/{id}/reactions", response_model=list[QuoteReaction]
)
def get_quote_reactions(
    id: int, session: Session = Depends(db.get_session)
) -> list[QuoteReaction]:
    return _get_quote_reactions(id, session)


@router.get(
    "/{id}/comments", response_model=list[QuoteCommentSchema]
)
def get_quote_comments(
    id: int,
    session: Session = Depends(db.get_session),
) -> list[QuoteComment]:
    return _get_quote_comments(id, session)


@router.post(
    "/{id}/comments/create", response_model=QuoteCommentSchema
)
def create_quote_comment(
    id: int,
    payload: CreateQuoteCommentBody,
    session: Session = Depends(db.get_session)
):
    return _create_quote_comment(id, payload.comment, payload.token, session)


@router.post(
    "/{id}/toggleReact", response_model=bool
)
def quote_toggle_react(
    id: int,
    payload: ToggleQuoteReactionBody,
    session: Session = Depends(db.get_session)
):
    return _quote_toggle_react(id, payload.reaction_name, payload.token, session)


@router.post(
    "/{id}/toggleSave", response_model=bool
)
def quote_toggle_save(
    id: int,
    payload: TokenBase,
    session: Session = Depends(db.get_session)
):
    return _quote_toggle_save(id, payload.token, session)
