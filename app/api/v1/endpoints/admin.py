from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams, get_pagination_params, verify_admin_api_key
from app.core.rate_limiter import limiter
from app.db.session import get_db
from app.schemas.ingestion_run import IngestionRunSummary
from app.schemas.pagination import PaginatedResponse
from app.services.ingestion_run_service import IngestionRunService

router = APIRouter()


@router.get("/ingestion-runs", response_model=PaginatedResponse[IngestionRunSummary])
@limiter.limit("60/minute")
def read_ingestion_runs(
    request: Request,
    pagination: PaginationParams = Depends(get_pagination_params),
    task_name: str | None = Query(None, description="Optional ingestion task filter"),
    status: str | None = Query(None, description="Optional ingestion status filter"),
    db: Session = Depends(get_db),
    _=Depends(verify_admin_api_key),
):
    items = IngestionRunService.list_runs(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        task_name=task_name,
        status=status,
    )
    total = IngestionRunService.count_runs(db, task_name=task_name, status=status)
    return {"items": items, "total": total, "skip": pagination.skip, "limit": pagination.limit}
