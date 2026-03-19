import os
import sys
import time

import redis
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


def wait_for_postgres(deadline: float) -> None:
    engine = create_engine(settings.sync_database_url, pool_pre_ping=True)
    while time.monotonic() < deadline:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except SQLAlchemyError:
            time.sleep(1)
    raise TimeoutError("Timed out waiting for PostgreSQL")


def wait_for_redis(deadline: float) -> None:
    client = redis.Redis.from_url(settings.REDIS_URL)
    try:
        while time.monotonic() < deadline:
            try:
                if client.ping():
                    return
            except redis.RedisError:
                time.sleep(1)
        raise TimeoutError("Timed out waiting for Redis")
    finally:
        client.close()


def main() -> int:
    deadline = time.monotonic() + settings.WAIT_FOR_SERVICES_TIMEOUT_SECONDS
    wait_for_postgres(deadline)
    wait_for_redis(deadline)
    print("Dependencies are reachable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
