from datetime import datetime, timedelta
from typing import Literal

from discord_webhook import DiscordWebhook, DiscordEmbed
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session, or_, and_

from api.v1.models.models import Quote, User, SavedQuote, QuoteReaction, QuoteComment, Webhook
from api.v1.schemas.quotes import QuoteSchema
from discord.main import DiscordOAuthHandler

dc_handler = DiscordOAuthHandler()


def _get_quotes(
    page: int,
    limit: int,
    search: str,
    sort: Literal["ascend", "descend"],
    token: str,
    session: Session,
):
    # Query quotes
    query = select(Quote).options(selectinload(Quote.user))

    if page and limit and page > 0 and limit > 0:
        query = query.limit(limit).offset((page - 1) * limit)

    if search:
        query = query.join(User).where(
            or_(
                Quote.quote.like(f"%{search}%"), User.display_name.like(f"%{search}%")
            )
        )

    if sort == "descend":
        query = query.order_by(Quote.created_at.desc())
    else:
        query = query.order_by(Quote.created_at)

    quotes = session.exec(query).all()

    if token:
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [quote.formatted_quote(user_info) for quote in quotes]
    return [quote.formatted_quote() for quote in quotes]


def _create_quote(
    quote: str,
    token: str,
    send_webhook: bool,
    session: Session,
):
    access_response = dc_handler.decode_token(token)

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        raise HTTPException(404, "User is not registered!")

    quote_obj = Quote(
        quote=quote, user_id=user.user_id, created_at=datetime.now()
    )

    session.add(quote_obj)
    session.flush()

    quote_dump: QuoteSchema = quote_obj.formatted_quote()

    session.commit()

    if send_webhook:
        # Post to Discord Webhook
        webhooks = session.exec(select(Webhook)).all()
        if not webhooks:
            return quote_dump

        webhook_urls = [f"{dc_handler.discord_api_endpoint}/webhooks/{webhook.webhook_id}/{webhook.webhook_token}" for
            webhook in webhooks]

        dc_webhooks = DiscordWebhook.create_batch(
            webhook_urls,
            avatar_url="https://quotly.eu/quotly512.png",
            username="Quotly"
        )

        embed = DiscordEmbed(
            title="Quotly",
            url=f"https://quotly.eu/quote/{quote_dump.get("quote_id")}",
            description=quote_dump.get("quote"),
            color=0xffffff,
            footer={
                "text": quote_dump.get("user").display_name,
                "icon_url": (f"https://cdn.discordapp.com/avatars/{quote_dump.get("user").discord_id}/"
                             f"{quote_dump.get("user").avatar_url}")
            }
        )
        for dc_webhook in dc_webhooks:
            dc_webhook.add_embed(embed)
            dc_webhook.execute()

    return quote_dump


def _get_top_quotes(
    limit: int,
    token: str,
    session: Session
):
    # Get top quotes of the last 30 days sorted by QuoteReaction count
    query = (select(Quote).outerjoin(Quote.reactions).where(
        Quote.created_at >= datetime.now() - timedelta(days=30)
    ).group_by(Quote.quote_id).order_by(func.count(Quote.reactions).desc()).limit(limit))

    quotes = session.exec(query).all()

    if token:
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [quote.formatted_quote(user_info) for quote in quotes]
    return [quote.formatted_quote() for quote in quotes]


def _get_quote(
    id: int,
    token: str,
    session: Session,
):
    quote = session.exec(select(Quote).where(Quote.quote_id == id)).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    if token:
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return quote.formatted_quote(user_info)
    return quote.formatted_quote()


def _delete_quote(
    id: int,
    token: str,
    session: Session
):
    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])

    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        raise HTTPException(404, "User is not registered!")

    quote = session.exec(select(Quote).where(Quote.quote_id == id)).first()
    if not quote:
        raise HTTPException(404, "Quote not found!")

    is_admin = False
    for role in user.roles:
        if role.role.name == "admin":
            is_admin = True

    if quote.user_id is not user.user_id or not is_admin:
        raise HTTPException(400, "Insufficient permissions!")

    session.delete(quote)
    session.commit()


def _is_quote_saved(
    id: int,
    token: str,
    session: Session
):
    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])

    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    quote = session.exec(select(Quote).where(Quote.quote_id == id)).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    saved = session.exec(
        select(SavedQuote).where(and_(SavedQuote.quote_id == quote.quote_id, SavedQuote.user_id == user.user_id))
    ).first()
    return saved


def _get_quote_reactions(
    id: int,
    session: Session,
):
    result = session.exec(select(QuoteReaction).where(QuoteReaction.quote_id == id)).all()
    return result


def _get_quote_comments(
    id: int,
    session: Session,
) -> list[QuoteComment]:
    result = session.exec(select(QuoteComment).where(QuoteComment.quote_id == id)).all()
    return result


def _create_quote_comment(
    id: int,
    comment: str,
    token: str,
    session: Session
):
    if not comment:
        raise HTTPException(400, "Required comment is empty!")

    if not token:
        raise HTTPException(400, "Required token is empty!")

    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        raise HTTPException(404, "User is not registered!")

    comment_object = QuoteComment(
        comment=comment, quote_id=id, user_id=user.user_id, created_at=datetime.now()
    )

    session.add(comment_object)
    session.flush()

    comment_dump = comment_object.model_dump()

    session.commit()

    return comment_dump


def _quote_toggle_react(
    id: int,
    reaction_name: Literal["red-heart", "thumbs-up", "face-with-tears-of-joy", "melting-face", "skull"],
    token: str,
    session: Session
):
    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])

    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    quote = session.exec(select(Quote).where(Quote.quote_id == id)).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    reaction = session.exec(
        select(QuoteReaction).where(
            and_(QuoteReaction.quote_id == quote.quote_id, QuoteReaction.user_id == user.user_id)
        )
    ).first()

    if reaction:
        if reaction.reaction_name == reaction_name:
            session.delete(reaction)
            session.commit()
            return False
        else:
            reaction.reaction_name = reaction_name
            session.commit()
            return True
    else:
        saved_object = QuoteReaction(
            user_id=user.user_id, quote_id=quote.quote_id, reaction_name=reaction_name
        )
        session.add(saved_object)
        session.commit()
        return True


def _quote_toggle_save(
    id: int,
    token: str,
    session: Session
):
    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])

    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    quote = session.exec(select(Quote).where(Quote.quote_id == id)).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    saved = session.exec(
        select(SavedQuote).where(and_(SavedQuote.quote_id == quote.quote_id, SavedQuote.user_id == user.user_id))
    ).first()
    if saved:
        session.delete(saved)
        session.commit()
    else:
        saved_object = SavedQuote(
            user_id=user.user_id, quote_id=quote.quote_id
        )
        session.add(saved_object)
        session.commit()

    return False if saved else True
