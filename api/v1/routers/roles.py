from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.v1.models.models import Role
from api.v1.tasks.roles import _get_roles, _get_role
from database.main import DatabaseHandler

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

db = DatabaseHandler()


@router.get(
    "",
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
    ),
    session: Session = Depends(db.get_session),
) -> list[Role]:
    return _get_roles(page, limit, session)


@router.get(
    "/{id}",
    response_model=Role
)
def get_role(
    id: int,
    session: Session = Depends(db.get_session),
) -> Role:
    return _get_role(id, session)
