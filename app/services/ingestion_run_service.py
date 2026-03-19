from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun


class IngestionRunService:
    @staticmethod
    def get_latest_run(db: Session) -> IngestionRun | None:
        return db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).first()

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
        error_count: int | None = None,
        error_message: str | None = None,
    ) -> IngestionRun:
        run.status = status
        run.report_date = report_date
        run.entries_total = entries_total
        run.entries_processed = entries_processed
        run.error_count = error_count
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
                IngestionRun.status == "success",
            )
            .order_by(IngestionRun.finished_at.desc())
            .first()
        )
