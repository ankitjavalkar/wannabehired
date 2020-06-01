from datetime import datetime

from django.apps import AppConfig
import django_rq


class ScraperConfig(AppConfig):
    name = 'wannabehired.apps.scraper'

    def ready(self):
        from .tasks import fetch_new_jobs_task

        scheduler = django_rq.get_scheduler('default')

        # Delete any existing jobs in the scheduler when the app starts up
        for job in scheduler.get_jobs():
            job.delete()

        # Have 'mytask' run every 5 minutes
        scheduler.schedule(datetime.utcnow(), fetch_new_jobs_task, interval=60*3)
