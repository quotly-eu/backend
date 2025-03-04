from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, or_, select

from api.v1.models.models import Quote, QuoteReaction, SavedQuote
from api.v1.models.models import Role, User, UserRole
from api.v1.schemas.quotes import QuoteSchema
from database.main import DatabaseHandler
from discord.main import DiscordOAuthHandler

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

db = DatabaseHandler()
dc_handler = DiscordOAuthHandler()

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
    query = select(User)

    if page and limit and page > 0 and limit > 0:
        query = query.limit(limit).offset(page - 1 * limit)

    if search:
        query = query.filter(User.display_name.like(f"%{search}%"))

    result = session.exec(query).all()

    return result


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
    access_response = dc_handler.decode_token(token)

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    return user.model_dump(by_alias=True)


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
    result = session.exec(select(User).where(or_(User.user_id == id, User.discord_id == id))).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get(
    "/{id}/quotes",
    response_model=list[QuoteSchema]
)
def get_user_quotes(
    id: int,
    sort: Literal["ascend", "descend"] | None = Query(
        default="descend",
        description="The order to sort the quotes by"
    ),
    token: str = Query(
        default=None,
        description="The JWT token"
    ),
    session: Session = Depends(db.get_session)
):
    user: User = session.exec(select(User).where(User.user_id == id)).first()
    if not user:
        raise HTTPException(404, "User not found!")

    # Sort quotes by created_at
    if sort == "ascend":
        user.quotes.sort(key=lambda quote: quote.created_at)
    else:
        user.quotes.sort(key=lambda quote: quote.created_at, reverse=True)

    if token:
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [quote.formatted_quote(user_info) for quote in user.quotes]
    return [quote.formatted_quote() for quote in user.quotes]


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
    result: list[QuoteReaction] = session.exec(select(QuoteReaction).where(QuoteReaction.user_id == id)).all()
    return result


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
    user_roles = session.exec(select(UserRole).where(UserRole.user_id == id)).all()
    return [user_role.role for user_role in user_roles]


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
    saved_quotes = session.exec(select(SavedQuote).where(SavedQuote.user_id == id)).all()

    if token:
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [saved_quote.quote.formatted_quote(user_info) for saved_quote in saved_quotes]
    return [saved_quote.quote.formatted_quote() for saved_quote in saved_quotes]
