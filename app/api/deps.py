from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.price_filters import PriceFilters, PriceSortField, SortOrder

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


class PaginationParams(BaseModel):
    skip: int
    limit: int


class AuthenticatedAPIKey(BaseModel):
    name: str
    scope: str


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of items to return"),
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)


def get_price_filters(
    report_date: Optional[date] = Query(None, description="Filter to a single report date"),
    start_date: Optional[date] = Query(None, description="Inclusive start date for historical queries"),
    end_date: Optional[date] = Query(None, description="Inclusive end date for historical queries"),
    commodity_id: Optional[UUID] = Query(None, description="Filter by commodity ID"),
    market_id: Optional[UUID] = Query(None, description="Filter by market ID"),
    category: Optional[str] = Query(None, description="Case-insensitive exact commodity category filter"),
    region: Optional[str] = Query(None, description="Case-insensitive exact market region filter"),
    sort_by: PriceSortField = Query(PriceSortField.REPORT_DATE, description="Primary sort field for price results"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort direction for the primary sort field"),
) -> PriceFilters:
    if report_date is not None and (start_date is not None or end_date is not None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="report_date cannot be combined with start_date or end_date",
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start_date cannot be later than end_date",
        )

    return PriceFilters(
        report_date=report_date,
        start_date=start_date,
        end_date=end_date,
        commodity_id=commodity_id,
        market_id=market_id,
        category=category.strip() if category and category.strip() else None,
        region=region.strip() if region and region.strip() else None,
        sort_by=sort_by,
        sort_order=sort_order,
    )


async def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
) -> AuthenticatedAPIKey:
    """
    Verify API key for protected endpoints.

    Protected write endpoints require a configured API key and a matching request header.
    """
    return await verify_service_api_key(x_api_key)


def _resolve_api_key(x_api_key: str) -> AuthenticatedAPIKey | None:
    for scope, scoped_keys in settings.protected_api_keys.items():
        for name, candidate in scoped_keys.items():
            if x_api_key == candidate:
                return AuthenticatedAPIKey(name=name, scope=scope)
    return None


def _scope_allows(principal_scope: str, required_scope: str) -> bool:
    if principal_scope == required_scope:
        return True
    return principal_scope == "admin" and required_scope == "service"


async def _verify_scoped_api_key(
    x_api_key: Optional[str],
    *,
    required_scope: str,
) -> AuthenticatedAPIKey:
    if not settings.has_protected_api_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Protected endpoint authentication is not configured on the server",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    principal = _resolve_api_key(x_api_key)
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not _scope_allows(principal.scope, required_scope):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient API key scope",
        )

    return principal


async def verify_service_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
) -> AuthenticatedAPIKey:
    return await _verify_scoped_api_key(x_api_key, required_scope="service")


async def verify_admin_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
) -> AuthenticatedAPIKey:
    return await _verify_scoped_api_key(x_api_key, required_scope="admin")


async def optional_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
) -> Optional[AuthenticatedAPIKey]:
    """
    Optional API key verification - returns the key if valid, None if not provided.
    Does not raise an error if key is missing.
    """
    if not x_api_key:
        return None

    return _resolve_api_key(x_api_key)


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )
