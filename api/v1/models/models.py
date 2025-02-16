from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from humps import camel

def to_camel(string):
  return camel.case(string)

class Base(SQLModel):
  class Config:
    alias_generator = to_camel

# Define the Quotes Table
class Quote(Base, table=True):
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

  user: "User" = Relationship(back_populates="quotes")
  reactions: list["QuoteReaction"] = Relationship(back_populates="quote")
  saved_quotes: list["SavedQuote"] = Relationship(back_populates="quote")
  comments: list["QuoteComment"] = Relationship(back_populates="quote")

class QuoteReaction(Base, table=True):
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

class SavedQuote(Base, table=True):
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
  user: "User" = Relationship(back_populates="saved_quotes")

class QuoteComment(Base, table=True):
  __tablename__ = "quote_comments"

  comment_id: int = Field(
    default=...,
    description="The saved quote identifier",
    primary_key=True
  )
  parent: int | None = Field(
    default=None,
    description="The parent comment identifier",
    foreign_key="quote_comments.comment_id"
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
  comment: str = Field(
    default=...,
    description="The comment text",
  )
  created_at: datetime = Field(
    default=datetime.now(),
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

  quote: "Quote" = Relationship(back_populates="comments")
  user: "User" = Relationship(back_populates="comments")


class Role(Base, table=True):
  __tablename__ = "roles"

  role_id: int = Field(
    default=...,
    description="The role's identifier",
    primary_key=True
  )
  name: str = Field(
    default=...,
    description="The role's name",
  )
  created_at: datetime = Field(
    default=...,
    description="The role's creation date",
  )

  user_roles: list["UserRole"] = Relationship(back_populates="role")


# Define the Users Table
class User(Base, table=True):
  __tablename__ = "users"

  user_id: int = Field(
    default=None,
    description="The user's identifier",
    primary_key=True,
  )
  discord_id: str = Field(
    default=...,
    description="The discord user's identifier",
  )
  email_address: str = Field(
    default=...,
    description="The user's email address",
    exclude=True,
  )
  display_name: str = Field(
    default=...,
    description="The user's name to display",
  )
  avatar_url: str = Field(
    default="",
    description="The user's name to display",
  )
  created_at: datetime = Field(
    default=datetime.now(),
    nullable=True,
    description="The user's creation date",
  )
  deleted_at: datetime | None = Field(
    default=None,
    nullable=True,
    description="The user's deletion date",
  )

  quotes: list["Quote"] = Relationship(back_populates="user")
  comments: list["QuoteComment"] = Relationship(back_populates="user")
  saved_quotes: list["SavedQuote"] = Relationship(back_populates="user")

class UserRole(Base, table=True):
  __tablename__ = "user_roles"

  id: int = Field(
    default=...,
    description="The user role row identifier",
    primary_key=True
  )
  user_id: str = Field(
    default=...,
    description="The user identifier",
    foreign_key="users.user_id"
  )
  role_id: str = Field(
    default=...,
    description="The role identifier",
    foreign_key="roles.role_id"
  )

  role: Role = Relationship(back_populates="user_roles")