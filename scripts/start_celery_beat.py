import os
import subprocess
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


def cleanup_schedule_artifacts() -> None:
    base = Path(settings.CELERY_BEAT_SCHEDULE_FILE)
    base.parent.mkdir(parents=True, exist_ok=True)
    candidates = [base, Path(f"{base}.bak"), Path(f"{base}.dat"), Path(f"{base}.dir")]
    for candidate in candidates:
        if candidate.exists():
            candidate.unlink()


def main() -> int:
    cleanup_schedule_artifacts()
    command = [sys.executable, "-m", "celery", "-A", "app.core.celery_app", "beat", "--loglevel=info"]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
