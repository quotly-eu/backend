from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from api.v1.models.models import Role
from database.main import DatabaseHandler

router = APIRouter(
  prefix="/roles",
  tags=["Roles"]
)

@router.get(
  "/",
  response_model=list[Role]
)
def get_roles(
  page: int = Query(
    default=None,
    description="The page number to retrieve starting from 1"
  ),
  limit: int = Query(
    default=None,
    description="The number of items to retrieve"
  )
) -> list[Role]:
  db = DatabaseHandler()

  query = select(Role)

  if page and limit and page > 0 and limit > 0:
    query = query.limit(limit).offset(page-1*limit)

  return db.session.exec(query).all()

@router.get(
  "/{id}",
  response_model=Role
)
def get_role(id: int) -> Role:
  db = DatabaseHandler()

  result = db.session.exec(select(Role).where(Role.role_id == id)).first()
  if not result:
    raise HTTPException(status_code=404, detail="Role not found")
  return result