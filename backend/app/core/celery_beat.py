from celery.schedules import crontab
from app.core.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "discover-every-morning": {
        "task": "app.scraper.tasks.discover_and_scrape",
        "schedule": crontab(hour=8, minute=0), # 8 AM daily
    },
}
