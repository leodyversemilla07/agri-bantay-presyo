from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IngestionRunSummary(BaseModel):
    id: UUID
    task_id: Optional[str] = None
    task_name: str
    status: str
    source_url: Optional[str] = None
    source_file: Optional[str] = None
    report_date: Optional[date] = None
    entries_total: Optional[int] = None
    entries_processed: Optional[int] = None
    entries_inserted: Optional[int] = None
    entries_updated: Optional[int] = None
    entries_skipped: Optional[int] = None
    error_count: Optional[int] = None
    error_message: Optional[str] = None
    anomaly_count: Optional[int] = None
    anomaly_flags: list[str] = Field(default_factory=list)
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
