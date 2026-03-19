import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text

from app.db.base_class import Base
from app.db.types import GUID


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    task_id = Column(String, index=True)
    task_name = Column(String, index=True, nullable=False)
    status = Column(String, index=True, nullable=False)
    source_url = Column(Text)
    source_file = Column(String, index=True)
    report_date = Column(Date, index=True)
    entries_total = Column(Integer)
    entries_processed = Column(Integer)
    entries_inserted = Column(Integer)
    entries_updated = Column(Integer)
    entries_skipped = Column(Integer)
    error_count = Column(Integer)
    anomaly_count = Column(Integer)
    anomaly_flags = Column(JSON, nullable=False, default=list)
    error_message = Column(Text)
    started_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    finished_at = Column(DateTime)
