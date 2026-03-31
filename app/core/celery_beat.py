from celery.schedules import crontab

from app.core.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "discover-8am": {
        "task": "app.scraper.tasks.discover_and_scrape",
        "schedule": crontab(hour=8, minute=0),
    },
    "discover-10am": {
        "task": "app.scraper.tasks.discover_and_scrape",
        "schedule": crontab(hour=10, minute=0),
    },
    "discover-12pm": {
        "task": "app.scraper.tasks.discover_and_scrape",
        "schedule": crontab(hour=12, minute=0),
    },
    "discover-2pm": {
        "task": "app.scraper.tasks.discover_and_scrape",
        "schedule": crontab(hour=14, minute=0),
    },
    "discover-4pm": {
        "task": "app.scraper.tasks.discover_and_scrape",
        "schedule": crontab(hour=16, minute=0),
    },
}
