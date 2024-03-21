from typing import List, Annotated

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: Annotated[int, Field(1, gt=0)]
    per_page: Annotated[int, Field(20, gt=0, le=100)]


class PaginationResponse(BaseModel):
    page: Annotated[int, Field(1, gt=0)]
    per_page: Annotated[int, Field(20, gt=0, le=100)]
    # pages: int = Query(gt=0)
    # total: int = Query(gt=0)
    items: List = []


async def paginate(session, pagination, query, schema):
    result = (await session.execute(
        query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    )).scalars()

    items = [schema.from_orm(item).dict() for item in result]
    for i in items:
        print(i)
    print(query)
    return PaginationResponse(
        page=pagination.page,
        per_page=pagination.per_page,
        items=items
    )
