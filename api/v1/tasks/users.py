from typing import Literal

import jwt
from fastapi import HTTPException
from requests import session
from sqlalchemy import Select
from sqlmodel import Session, or_, select

from api.v1.models.models import Quote, QuoteReaction, SavedQuote, Webhook
from api.v1.models.models import Role, User, UserRole
from api.v1.schemas.quotes import QuoteSchema
from config.main import parser
from discord.main import DiscordOAuthHandler

dc_handler = DiscordOAuthHandler()


def _get_users(
    page: int,
    limit: int,
    search: str,
    session: Session,
) -> list[User]:
    query = select(User)

    if page and limit and page > 0 and limit > 0:
        query = query.limit(limit).offset(page - 1 * limit)

    if search:
        query = query.filter(User.display_name.like(f"%{search}%"))

    result = session.exec(query).all()

    return result


def _get_me(
    token: str,
    session: Session,
) -> User:
    access_response = dc_handler.decode_token(token)

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    return user.model_dump()


def _delete_me(
    token: str,
    session: Session,
) -> User:
    access_response = dc_handler.decode_token(token)

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        raise HTTPException(404, "User not found!")

    user_dump = user.model_dump()
    session.delete(user)
    session.commit()

    return user_dump


def _get_user(
    id: int,
    session: Session,
) -> User:
    result = session.exec(select(User).where(or_(User.user_id == id, User.discord_id == id))).first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


def _get_user_quotes(
    id: int,
    sort: Literal["ascend", "descend"],
    token: str,
    session: Session
) -> list[QuoteSchema]:
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


def _get_user_reactions(
    id: int,
    session: Session,
) -> list[QuoteReaction]:
    result: list[QuoteReaction] = session.exec(select(QuoteReaction).where(QuoteReaction.user_id == id)).all()
    return result


def _get_user_roles(
    id: int,
    session: Session,
) -> list[Role]:
    user_roles = session.exec(select(UserRole).where(UserRole.user_id == id)).all()
    return [user_role.role for user_role in user_roles]


def _get_user_saved_quotes(
    id: int,
    token: str,
    session: Session,
) -> list[Quote]:
    saved_quotes = session.exec(select(SavedQuote).where(SavedQuote.user_id == id)).all()

    if token:
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [saved_quote.quote.formatted_quote(user_info) for saved_quote in saved_quotes]
    return [saved_quote.quote.formatted_quote() for saved_quote in saved_quotes]

def _get_webhooks(
    token: str,
    session: Session,
) -> list[Webhook]:
    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()
    if not user:
        raise HTTPException(404, "User not found!")
    webhooks = session.exec(select(Webhook).where(Webhook.user_id == user.user_id)).all()
    return webhooks

def _create_webhook(
    code: str,
    session: Session
):
    key = parser.get("JWT", "key")

    access_response = dc_handler.receive_access_response(code, dc_handler.redirect_uri_webhook)
    webhook = access_response.get("webhook")
    if not webhook:
        raise HTTPException(404, "Webhook not found!")

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()
    if not user:
        raise HTTPException(404, "User not found!")

    webhook_obj = Webhook(
        user_id=user.user_id,
        webhook_id=webhook["id"],
        webhook_token=webhook["token"],
    )
    session.add(webhook_obj)
    session.commit()

    return jwt.encode(access_response, key)

def _delete_webhook(
    token: str,
    id: int,
    session: Session,
):
    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()
    if not user:
        raise HTTPException(404, "User not found!")

    webhook = session.exec(select(Webhook).where(Webhook.id == id)).first()
    if not webhook:
        raise HTTPException(404, "Webhook not found!")

    session.delete(webhook)
    session.commit()