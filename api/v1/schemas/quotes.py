from datetime import datetime
from typing import Literal, Optional, Union

from humps import camel
from pydantic import BaseModel, Field

from api.v1.models.models import Quote, User
from api.v1.schemas.discord import TokenBase


def to_camel(string):
    return camel.case(string)


class Base(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class QuoteSchema(Base):
    quote: str = Field(
        default=None,
        description="The quote text"
    )
    quote_id: int = Field(
        default=...,
        description="The quote identifier",
    )
    user_id: int = Field(
        default=...,
        description="The user identifier",
    )
    created_at: datetime = Field(
        default=datetime.now(),
        description="The quote creation date",
    )
    changed_at: datetime | None = Field(
        default=None,
        description="The quote last change date",
    )
    deleted_at: datetime | None = Field(
        default=None,
        description="The quote deletion date",
    )

    is_saved: Optional[bool] = Field(
        default=False,
        description="The quote is saved by the user",
    )
    reaction: Optional[str] = Field(
        default=None,
        description="The user's reaction to the quote",
    )

    user: Union[User, None] = None
    reactions: list["QuoteReactionSchema"] = []


class QuoteCommentSchema(Base):
    comment_id: int = Field(
        default=...,
        description="The saved quote identifier",
    )
    parent: int | None = Field(
        default=None,
        description="The parent comment identifier",
    )
    quote_id: int = Field(
        default=...,
        description="The quote identifier",
    )
    comment: str = Field(
        default=...,
        description="The comment text",
    )
    created_at: datetime = Field(
        default=...,
        description="The user's creation date",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="The user's last update date",
    )
    deleted_at: datetime | None = Field(
        default=None,
        description="The user's deletion date",
    )

    user: Union[User, None] = None


class QuoteReactionSchema(Base):
    reaction_name: Literal["red-heart", "thumbs-up", "face-with-tears-of-joy", "melting-face", "skull"] = Field(
        default=...,
        description="The reaction name",
    )
    count: int = Field(
        default=0,
        description="The reaction count",
    )


class SavedQuoteSchema(Base):
    saved_id: int = Field(
        default=...,
        description="The saved quote identifier",
    )
    quote: Union[Quote, None] = None
    user: Union[User, None] = None

class CreateQuoteBody(TokenBase):
    quote: str = Field(default=..., description="The quote markdown text"),
    send_webhook: bool = Field(
        default=False, description="Send the quote to the Discord webhooks?"
    ),
    
class CreateQuoteCommentBody(TokenBase):
    comment: str = Field(default=..., description="Comment's text"),
    
class ToggleQuoteReactionBody(TokenBase):
    reaction_name: Literal["red-heart", "thumbs-up", "face-with-tears-of-joy", "melting-face", "skull"] = Field(
        default=..., 
        description="The reaction name"
    ),