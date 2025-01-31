from fastapi import APIRouter
from sqlmodel import select
from api.v1.models.quotes import Quote
from database.main import DatabaseHandler

router = APIRouter(
  prefix="/quotes",
  tags=["Quotes"]
)

@router.get("/")
def get_quotes() -> list[Quote]:
  db = DatabaseHandler()

  return db.session.exec(select(Quote)).all()