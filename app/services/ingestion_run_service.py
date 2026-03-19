from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun


class IngestionRunService:
    @staticmethod
    def _base_query(
        db: Session,
        *,
        task_name: str | None = None,
        status: str | None = None,
    ):
        query = db.query(IngestionRun)
        if task_name:
            query = query.filter(IngestionRun.task_name == task_name)
        if status:
            query = query.filter(IngestionRun.status == status)
        return query

    @staticmethod
    def get_latest_run(db: Session) -> IngestionRun | None:
        return db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).first()

    @staticmethod
    def list_runs(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        task_name: str | None = None,
        status: str | None = None,
    ) -> list[IngestionRun]:
        return (
            IngestionRunService._base_query(db, task_name=task_name, status=status)
            .order_by(IngestionRun.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_runs(
        db: Session,
        *,
        task_name: str | None = None,
        status: str | None = None,
    ) -> int:
        return IngestionRunService._base_query(db, task_name=task_name, status=status).count()

    @staticmethod
    def start_run(
        db: Session,
        task_name: str,
        task_id: str | None = None,
        source_url: str | None = None,
        source_file: str | None = None,
    ) -> IngestionRun:
        if task_id:
            existing = db.query(IngestionRun).filter(IngestionRun.task_id == task_id).first()
            if existing:
                return existing

        run = IngestionRun(
            task_id=task_id,
            task_name=task_name,
            status="running",
            source_url=source_url,
            source_file=source_file,
            started_at=datetime.now(UTC).replace(tzinfo=None),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def finish_run(
        db: Session,
        run: IngestionRun,
        *,
        status: str,
        report_date=None,
        entries_total: int | None = None,
        entries_processed: int | None = None,
        entries_inserted: int | None = None,
        entries_updated: int | None = None,
        entries_skipped: int | None = None,
        error_count: int | None = None,
        anomaly_count: int | None = None,
        anomaly_flags: list[str] | None = None,
        error_message: str | None = None,
    ) -> IngestionRun:
        run.status = status
        run.report_date = report_date
        run.entries_total = entries_total
        run.entries_processed = entries_processed
        run.entries_inserted = entries_inserted
        run.entries_updated = entries_updated
        run.entries_skipped = entries_skipped
        run.error_count = error_count
        run.anomaly_count = anomaly_count
        run.anomaly_flags = anomaly_flags or []
        run.error_message = error_message
        run.finished_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get_latest_successful_scrape(db: Session) -> IngestionRun | None:
        return (
            db.query(IngestionRun)
            .filter(
                IngestionRun.task_name == "scrape_daily_prices",
                IngestionRun.status.in_(("success", "partial_success")),
            )
            .order_by(IngestionRun.finished_at.desc())
            .first()
        )

    @staticmethod
    def get_recent_successful_scrapes(db: Session, *, limit: int = 5) -> list[IngestionRun]:
        return (
            db.query(IngestionRun)
            .filter(
                IngestionRun.task_name == "scrape_daily_prices",
                IngestionRun.status.in_(("success", "partial_success")),
                IngestionRun.entries_total.isnot(None),
                (IngestionRun.anomaly_count.is_(None) | (IngestionRun.anomaly_count == 0)),
            )
            .order_by(IngestionRun.finished_at.desc())
            .limit(limit)
            .all()
        )
