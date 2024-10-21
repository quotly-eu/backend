from sqlmodel import Field, SQLModel
from datetime import datetime

# Define the Quotes Table
class Quote(SQLModel, table=True):
  quote: str = Field(
    default=...,
    description="The quote text",
    examples=["**First Quote**"]
  )
  quote_id: int = Field(
    default=...,
    description="The quote identifier",
    examples=[1],
    primary_key=True
  )
  user_id: int = Field(
    default=...,
    description="The user identifier",
    examples=[1]
  )
  created_at: datetime = Field(
    default=...,
    description="The quote creation date",
    examples=[datetime.now()]
  )
  changed_at: datetime | None = Field(
    default=None,
    description="The quote last change date",
    examples=[datetime.now()]
  )
  deleted_at: datetime | None = Field(
    default=None,
    description="The quote deletion date",
    examples=[datetime.now()]
  )