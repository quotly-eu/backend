from fastapi import HTTPException
from sqlmodel import Session, select

from api.v1.models.models import Role


def _get_roles(
    page: int,
    limit: int,
    session: Session,
) -> list[Role]:
    query = select(Role)

    if page and limit and page > 0 and limit > 0:
        query = query.limit(limit).offset(page - 1 * limit)

    return session.exec(query).all()


def _get_role(
    id: int,
    session: Session,
) -> Role:
    result = session.exec(select(Role).where(Role.role_id == id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Role not found")
    return result
