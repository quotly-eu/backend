from datetime import datetime
from typing import Union
from pydantic import BaseModel, Field

from api.v1.models.models import Quote, QuoteReaction, User

from humps import camel

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

  user: Union[User, None] = None
  reactions: list[QuoteReaction] = []

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

class SavedQuoteSchema(Base):
  saved_id: int = Field(
    default=...,
    description="The saved quote identifier",
  )
  quote: Union[Quote, None] = None
  user: Union[User, None] = None