from typing import Literal

from fastapi import APIRouter, Depends, Path, Query, Form
from sqlmodel import Session

from api.v1.models.models import Quote, QuoteReaction, Webhook
from api.v1.models.models import Role, User
from api.v1.schemas.quotes import QuoteSchema
from api.v1.tasks.users import (
    _get_users,
    _get_me,
    _delete_me,
    _get_user,
    _get_user_quotes,
    _get_user_reactions,
    _get_user_roles,
    _get_user_saved_quotes,
    _create_webhook,
    _get_webhooks, _delete_webhook
)
from database.main import DatabaseHandler

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

db = DatabaseHandler()


@router.get("", response_model=list[User])
def get_users(
    page: int = Query(
        default=None,
        description="The page number to retrieve starting from 1"
    ),
    limit: int = Query(
        default=None,
        description="The number of items to retrieve"
    ),
    search: str = Query(
        default=None,
        description="The search term to filter users by"
    ),
    session: Session = Depends(db.get_session),
) -> list[User]:
    return _get_users(page, limit, search, session)


@router.get(
    "/me",
    response_model=User
)
def get_me(
    token: str = Query(
        default=...,
        description="The JWT token"
    ),
    session: Session = Depends(db.get_session),
) -> User:
    return _get_me(token, session)


@router.delete(
    "/me/delete",
    response_model=User
)
def delete_me(
    token: str = Form(
        default=...,
        description="The JWT token"
    ),
    session: Session = Depends(db.get_session),
) -> User:
    return _delete_me(token, session)


@router.get(
    "/{id}",
    response_model=User,
)
def get_user(
    id: int = Path(
        default=...,
        description="The user or discord user identifier"
    ),
    session: Session = Depends(db.get_session),
) -> User:
    return _get_user(id, session)


@router.get(
    "/{id}/quotes",
    response_model=list[QuoteSchema]
)
def get_user_quotes(
    id: int = Path(
        default=...,
        description="The user identifier"
    ),
    sort: Literal["ascend", "descend"] = Query(
        default="descend",
        description="The order to sort the quotes by"
    ),
    token: str = Query(
        default=None,
        description="The JWT token"
    ),
    session: Session = Depends(db.get_session)
):
    return _get_user_quotes(id, sort, token, session)


@router.get(
    "/{id}/reactions",
    response_model=list[QuoteReaction]
)
def get_user_reactions(
    id: int = Path(
        default=...,
        description="The user identifier"
    ),
    session: Session = Depends(db.get_session),
) -> list[QuoteReaction]:
    return _get_user_reactions(id, session)


@router.get(
    "/{id}/roles",
    response_model=list[Role]
)
def get_user_roles(
    id: int = Path(
        default=...,
        description="The user identifier"
    ),
    session: Session = Depends(db.get_session),
) -> list[Role]:
    return _get_user_roles(id, session)


@router.get(
    "/{id}/saved-quotes",
    response_model=list[QuoteSchema]
)
def get_user_saved_quotes(
    id: int = Path(
        default=...,
        description="The user identifier"
    ),
    token: str = Query(
        default=None,
        description="The JWT token"
    ),
    session: Session = Depends(db.get_session),
) -> list[Quote]:
    return _get_user_saved_quotes(id, token, session)


@router.post(
    "/webhook"
)
def create_webhook(
    code: str = Form(
        ...,
        description="The code response from discord"
    ),
    session: Session = Depends(db.get_session),
):
    return _create_webhook(code, session)

@router.get(
    "/me/webhooks",
    response_model=list[Webhook]
)
def get_webhooks(
    token: str = Query(
        default=...,
        description="The JWT token"
    ),
    session: Session = Depends(db.get_session),
):
    return _get_webhooks(token, session)

@router.delete(
    "/webhook"
)
def create_webhook(
    token: str = Form(
        ...,
        description="The JWT token"
    ),
    id: int = Form(
        ...,
        description="The webhook db identifier"
    ),
    session: Session = Depends(db.get_session),
):
    return _delete_webhook(token, id, session)