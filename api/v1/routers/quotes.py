from fastapi import APIRouter
from api.v1.schemas import quotes

router = APIRouter(
  prefix="/quotes",
  tags=["Quotes"]
)

@router.get("/")
def get_quotes() -> list[quotes.Quote]:
  return [
    {
      "quote": "first quote",
      "quote_id": 1,
      "user_id": 1,
      "created_at": "2021-10-10T10:10:10",
      "changed_at": None,
      "deleted_at": None
    },
    {
      "quote": "second quote",
      "quote_id": 2,
      "user_id": 1,
      "created_at": "2021-10-10T10:10:10",
      "changed_at": None,
      "deleted_at": None
    }
  ]