from datetime import datetime
from pydantic import Field, StrictInt, StrictStr
from api.v1.schemas.main import BaseModel

class Quote(BaseModel):
  quote: StrictStr = Field(
    default=...,
    description="The quote text",
    examples=["**First Quote**"]
  )
  quote_id: StrictInt = Field(
    default=...,
    description="The quote identifier",
    examples=[1],
    alias="quoteId"
  )
  user_id: StrictInt = Field(
    default=...,
    description="The user identifier",
    examples=[1],
    alias="userId"
  )
  created_at: datetime = Field(
    default=...,
    description="The quote creation date",
    examples=[datetime.now()],
    alias="createdAt"
  )
  changed_at: datetime | None = Field(
    default=None,
    description="The quote last change date",
    examples=[datetime.now()],
    alias="changedAt"
  )
  deleted_at: datetime | None = Field(
    default=None,
    description="The quote deletion date",
    examples=[datetime.now()],
    alias="deletedAt"
  )
  