#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d db redis
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" run --rm api python scripts/wait_for_services.py

./scripts/backup_db.sh

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" run --rm api python scripts/preflight_duplicates.py
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" run --rm api alembic upgrade head

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d api worker beat caddy

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T api python scripts/health_check.py --mode ready --production --quiet
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T api python scripts/health_check.py --production --quiet

echo "Production deployment completed successfully."
