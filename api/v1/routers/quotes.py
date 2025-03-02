from datetime import datetime, timedelta
from typing import Literal, Union

from discord_webhook import DiscordEmbed, DiscordWebhook
from fastapi import APIRouter, Depends, Form, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, and_, func, or_, select

from api.v1.models.models import Quote, QuoteComment, QuoteReaction, SavedQuote, User
from api.v1.schemas.quotes import QuoteCommentSchema, QuoteSchema, SavedQuoteSchema
from database.main import DatabaseHandler
from discord.main import DiscordOAuthHandler

router = APIRouter(
    prefix="/quotes",
    tags=["Quotes"]
)

db = DatabaseHandler()


@router.get(
    "",
    response_model=list[QuoteSchema]
)
def get_quotes(
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
        description="The search term to filter quotes by",
    ),
    sort: Literal["ascend", "descend"] | None = Query(
        default="descend",
        description="The order to sort the quotes by"
    ),
    token: str = Query(
        default=None,
        description="The JWT token from the current user"
    ),
    session: Session = Depends(db.get_session),
):
    # Query quotes
    query = select(Quote).options(selectinload(Quote.user))

    if page and limit and page > 0 and limit > 0:
        query = query.limit(limit).offset((page - 1) * limit)

    if search:
        query = query.join(User).where(
            or_(
                Quote.quote.like(f"%{search}%"),
                User.display_name.like(f"%{search}%")
            )
        )

    if sort == "descend":
        query = query.order_by(Quote.created_at.desc())
    else:
        query = query.order_by(Quote.created_at)

    quotes = session.exec(query).all()

    if token:
        dc_handler = DiscordOAuthHandler()
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [quote.formatted_quote(user_info) for quote in quotes]
    return [quote.formatted_quote() for quote in quotes]


@router.post(
    "/create",
    response_model=QuoteSchema
)
def create_quote(
    quote: str = Form(..., description="The quote markdown text"),
    token: str = Form(..., description="The JWT token from the current user"),
    send_webhook: bool = Form(
        default=False,
        description="Send the quote to the Discord webhook"
    ),
    session: Session = Depends(db.get_session),
):
    dc_handler = DiscordOAuthHandler()

    access_response = dc_handler.decode_token(token)

    user_info = dc_handler.receive_user_information(access_response["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        raise HTTPException(404, "User is not registered!")

    quote_obj = Quote(
        quote=quote,
        user_id=user.user_id,
        created_at=datetime.now()
    )

    session.add(quote_obj)
    session.flush()

    quote_dump: QuoteSchema = quote_obj.formatted_quote()

    session.commit()

    if send_webhook:
        # Post to Discord Webhook
        webhook = DiscordWebhook(
            url=dc_handler.webhook_url,
            avatar_url="https://quotly.eu/quotly512.png",
            username="Quotly",
        )
        embed = DiscordEmbed(
            title= "Quotly",
            url=f"https://quotly.eu/quote/{quote_dump.get("quote_id")}",
            description=quote_dump.get("quote"),
            color=0xffffff,
            footer={
                "text": quote_dump.get("user").display_name,
                "icon_url": (
                    f"https://cdn.discordapp.com/avatars/{quote_dump.get("user").discord_id}/"
                    f"{quote_dump.get("user").avatar_url}"
                )
            }
        )
        webhook.add_embed(embed)
        webhook.execute()

    return quote_dump


@router.delete(
    "/{id}/delete",
    response_model=None
)
def delete_quote(
    id: int,
    token: str = Form(..., description="The JWT token from the current user"),
    session: Session = Depends(db.get_session)
):
    dc_handler = DiscordOAuthHandler()
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
        raise HTTPException(400, "Unsufficient permissions!")

    session.delete(quote)
    session.commit()


@router.get(
    "/top",
    response_model=list[QuoteSchema],
)
def get_top_quotes(
    limit: int = Query(
        default=10,
        description="The number of top quotes to retrieve"
    ),
    token: str = Query(
        default=None,
        description="The JWT token from the current user"
    ),
    session: Session = Depends(db.get_session),
):
    # Get top quotes of the last 30 days sorted by QuoteReaction count
    query = (
        select(Quote)
        .outerjoin(Quote.reactions)
        .where(Quote.created_at >= datetime.now() - timedelta(days=30))
        .group_by(Quote.quote_id)
        .order_by(func.count(Quote.reactions).desc())
        .limit(limit)
    )

    quotes = session.exec(query).all()

    if token:
        dc_handler = DiscordOAuthHandler()
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return [quote.formatted_quote(user_info) for quote in quotes]
    return [quote.formatted_quote() for quote in quotes]


@router.get(
    "/{id}",
    response_model=QuoteSchema
)
def get_quote(
    id: int,
    token: str = Query(
        default=None,
        description="The JWT token from the current user"
    ),
    session: Session = Depends(db.get_session),
):
    quote = session.exec(select(Quote).where(Quote.quote_id == id)).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    if token:
        dc_handler = DiscordOAuthHandler()
        user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
        return quote.formatted_quote(user_info)
    return quote.formatted_quote()


@router.get(
    "/{id}/saved",
    response_model=Union[SavedQuoteSchema, None]
)
def is_quote_saved(
    id: int,
    token: str = Query(..., description="The JWT token from the current user"),
    session: Session = Depends(db.get_session)
):
    dc_handler = DiscordOAuthHandler()
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


@router.post(
    "/{id}/toggleReact",
    response_model=bool
)
def quote_toggle_react(
    id: int,
    reaction_name: Literal["red-heart", "thumbs-up", "face-with-tears-of-joy", "melting-face", "skull"] = Form(
        ...,
        description="The reaction name"
    ),
    token: str = Form(..., description="The JWT token from the current user"),
    session: Session = Depends(db.get_session)
):
    dc_handler = DiscordOAuthHandler()
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
            user_id=user.user_id,
            quote_id=quote.quote_id,
            reaction_name=reaction_name
        )
        session.add(saved_object)
        session.commit()
        return True


@router.post(
    "/{id}/toggleSave",
    response_model=bool
)
def quote_toggle_save(
    id: int,
    token: str = Form(..., description="The JWT token from the current user"),
    session: Session = Depends(db.get_session)
):
    dc_handler = DiscordOAuthHandler()
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
            user_id=user.user_id,
            quote_id=quote.quote_id
        )
        session.add(saved_object)
        session.commit()

    return False if saved else True


@router.get(
    "/{id}/reactions",
    response_model=list[QuoteReaction]
)
def get_quote_reactions(
    id: int,
    session: Session = Depends(db.get_session)
) -> list[QuoteReaction]:
    result = session.exec(select(QuoteReaction).where(QuoteReaction.quote_id == id)).all()
    return result


@router.get(
    "/{id}/comments",
    response_model=list[QuoteCommentSchema]
)
def get_quote_comments(
    id: int,
    session: Session = Depends(db.get_session),
) -> list[QuoteComment]:
    result = session.exec(select(QuoteComment).where(QuoteComment.quote_id == id)).all()
    return result


@router.post(
    "/{id}/comments/create",
    response_model=QuoteCommentSchema
)
def create_quote_comment(
    id: int,
    comment: str = Form(..., description="Comment's text"),
    token: str = Form(..., description="The JWT token from the current user"),
    session: Session = Depends(db.get_session)
):
    if not comment:
        raise HTTPException(400, "Required comment is empty!")

    if not token:
        raise HTTPException(400, "Required token is empty!")

    dc_handler = DiscordOAuthHandler()

    user_info = dc_handler.receive_user_information(dc_handler.decode_token(token)["access_token"])
    user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

    if not user:
        raise HTTPException(404, "User is not registered!")

    comment_object = QuoteComment(
        comment=comment,
        quote_id=id,
        user_id=user.user_id,
        created_at=datetime.now()
    )

    session.add(comment_object)
    session.flush()

    comment_dump = comment_object.model_dump()

    session.commit()

    return comment_dump
