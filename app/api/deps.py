from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    skip: int
    limit: int


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of items to return"),
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)
