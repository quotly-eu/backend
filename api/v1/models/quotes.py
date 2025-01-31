from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

# Define the Quotes Table
class Quote(SQLModel, table=True):
  __tablename__ = "quotes"

  quote: str = Field(
    default=...,
    description="The quote text"
  )
  quote_id: int = Field(
    default=...,
    description="The quote identifier",
    primary_key=True
  )
  user_id: int = Field(
    default=...,
    description="The user identifier",
    foreign_key="users.user_id"
  )
  created_at: datetime = Field(
    default=...,
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

  reactions: list["QuoteReaction"] = Relationship(back_populates="quote")
  saved_quotes: list["SavedQuote"] = Relationship(back_populates="quote")


class QuoteReaction(SQLModel, table=True):
  __tablename__ = "quote_reactions"

  reaction_id: int = Field(
    default=...,
    description="The reaction identifier",
    primary_key=True
  )
  user_id: int = Field(
    default=...,
    description="The user's identifier",
    foreign_key="users.user_id"
  )
  quote_id: str = Field(
    default=...,
    description="The quote identifier",
    foreign_key="quotes.quote_id",
  )
  reaction_name: str = Field(
    default=...,
    description="The reaction name",
  )
  created_at: datetime = Field(
    default=...,
    description="The user's creation date",
  )
  quote: Quote = Relationship(back_populates="reactions")

class SavedQuote(SQLModel, table=True):
  __tablename__ = "saved_quotes"

  saved_id: int = Field(
    default=...,
    description="The saved quote identifier",
    primary_key=True
  )
  user_id: int = Field(
    default=...,
    description="The user's identifier",
    foreign_key="users.user_id"
  )
  quote_id: int = Field(
    default=...,
    description="The quote identifier",
    foreign_key="quotes.quote_id",
  )
  quote: Quote = Relationship(back_populates="saved_quotes")
