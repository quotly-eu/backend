
from pydantic import BaseModel, Field
from humps import camel


def to_camel(string):
    return camel.case(string)


class Base(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True

class TokenBase(Base):
    token: str = Field(
        default=...,
        description="The JWT token from the current user"
    )

class AuthorizeBody(Base):
    code: str = Field(
        default=...,
        description="Authorization code received from Discord", 
        example="1234567890"
    ),

class WebhookDeleteBody(TokenBase):
    id: int = Field(
        default=...,
        description="The webhook db identifier"
    ),
    