from datetime import datetime, timedelta
from typing import Literal
from fastapi import APIRouter, Depends, Form, HTTPException, Query
from sqlmodel import Session, func, or_, select
from api.v1.models.models import Quote, QuoteComment, QuoteReaction, User
from api.v1.schemas.quotes import QuoteCommentSchema, QuoteSchema
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
    default="ascend",
    description="The order to sort the quotes by"
  ),
  session: Session = Depends(db.get_session),
) -> list[Quote]:
  query = select(Quote)

  if page and limit and page > 0 and limit > 0:
    query = query.limit(limit).offset(page-1*limit)
  
  if search:
    query = query.filter(or_(
      Quote.quote.like(f"%{search}%"),
      Quote.user_id.like(f"%{search}%"),
      Quote.user.display_name.like(f"%{search}%")
    ))

  if sort == "descend":
    query = query.order_by(Quote.created_at.desc())
  else:
    query = query.order_by(Quote.created_at)

  return session.exec(query).all()

@router.post(
    "/create",
    response_model=QuoteSchema
)
def create_quote(
  quote: str = Form(..., description="The quote markdown text"),
  token: str = Form(..., description="The JWT token from the current user"),
  session: Session = Depends(db.get_session),
): 
  dc_handler = DiscordOAuthHandler()

  access_response = dc_handler.decode_token(token)
  
  user_info = dc_handler.receive_user_information(access_response["access_token"])
  user = session.exec(select(User).where(User.discord_id == user_info["id"])).first()

  if not user:
    raise HTTPException(404, "User is not registered!")
  
  quote_object = Quote(
    quote=quote,
    user_id=user.user_id,
  )

  session.add(quote_object)
  session.flush()
  
  quote_dump = quote_object.model_dump()

  session.commit()

  return quote_dump

@router.get(
  "/top",
  response_model=list[QuoteSchema],
)
def get_top_quotes(
  limit: int = Query(
    default=10,
    description="The number of top quotes to retrieve"
  ),
  session: Session = Depends(db.get_session),
) -> list[QuoteSchema]:
  # Get top quotes of the last 30 days sorted by QuoteReaction count
  query = (
    select(Quote)
    .outerjoin(Quote.reactions)
    .where(Quote.created_at >= datetime.now() - timedelta(days=30))
    .group_by(Quote.quote_id)
    .order_by(func.count(Quote.reactions).desc())
    .limit(limit)
  )

  result = session.exec(query).all()
  return result

@router.get(
  "/{id}",
  response_model=QuoteSchema
)
def get_quote(
  id: int,
  session: Session = Depends(db.get_session),
) -> Quote:
  result = session.exec(select(Quote).where(Quote.quote_id == id)).first()
  if not result:
    raise HTTPException(status_code=404, detail="Quote not found")
  return result

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