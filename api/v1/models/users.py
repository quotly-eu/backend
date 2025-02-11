from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

# Define the Users Table
class User(SQLModel, table=True):
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

class UserRole(SQLModel, table=True):
  __tablename__ = "user_roles"

  id: int = Field(
    default=...,
    description="The user role row identifier",
    primary_key=True
  )
  user_id: str = Field(
    default=...,#
    description="The user identifier",
    foreign_key="users.user_id"
  )
  role_id: str = Field(
    default=...,
    description="The role identifier",
    foreign_key="roles.role_id"
  )