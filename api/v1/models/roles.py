from sqlmodel import Field, SQLModel
from datetime import datetime

# Define the Users Table
class Role(SQLModel, table=True):
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
