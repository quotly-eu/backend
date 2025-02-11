from datetime import datetime, timedelta
from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import or_, select
from api.v1.models.models import Quote, QuoteComment, QuoteReaction
from database.main import DatabaseHandler

router = APIRouter(
  prefix="/quotes",
  tags=["Quotes"]
)

@router.get(
  "/",
  response_model=list[Quote]
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
  )
) -> list[Quote]:
  db = DatabaseHandler()

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

  return db.session.exec(query).all()

@router.get(
  "/{id}",
  response_model=Quote
)
def get_quote(id: int) -> Quote:
  db = DatabaseHandler()

  result = db.session.exec(select(Quote).where(Quote.quote_id == id)).first()
  if not result:
    raise HTTPException(status_code=404, detail="Quote not found")
  return result

@router.get(
  "/{id}/reactions",
  response_model=list[QuoteReaction]
)
def get_quote_reactions(id: int) -> list[QuoteReaction]:
  db = DatabaseHandler()

  result = db.session.exec(select(QuoteReaction).where(QuoteReaction.quote_id == id)).all()
  return result

@router.get(
  "/{id}/comments",
  response_model=list[QuoteComment]
)
def get_quote_comments(id: int) -> list[QuoteComment]:
  db = DatabaseHandler()

  result = db.session.exec(select(QuoteComment).where(QuoteComment.quote_id == id)).all()
  return result

@router.get(
  "/top",
  response_model=list[Quote],
)
def get_top_quotes(
  limit: int = Query(
    default=10,
    description="The number of top quotes to retrieve"
  )
) -> list[Quote]:
  db = DatabaseHandler()

  # Get top quotes of the last 30 days sorted by QuoteReaction count
  query = select(Quote).where(
    Quote.created_at >= datetime.now() - timedelta(days=30)
  ).order_by(
    Quote.reactions.count()
  ).limit(limit)

  result = db.session.exec(query).all()
  return result