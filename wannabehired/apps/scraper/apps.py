from datetime import datetime

from django.apps import AppConfig
import django_rq


class ScraperConfig(AppConfig):
    name = 'wannabehired.apps.scraper'

    def ready(self):
        from .tasks import (update_jobs_in_latest_wih_thread_task,
            update_jobs_in_latest_fsf_thread_task,
            update_jobs_in_latest_wwtbh_thread_task,
            update_new_threads_task
        )

        scheduler = django_rq.get_scheduler('default')

        # Delete any existing jobs in the scheduler when the app starts up
        for job in scheduler.get_jobs():
            job.delete()

        # Delete any existing jobs in the queue when the app starts up
        default_queue = django_rq.get_queue('default')
        for job in default_queue.get_jobs():
            job.delete()

        scheduler.cron(
            '5 16 * * *',
            update_new_threads_task,
            queue_name='default',
        )

        scheduler.schedule(
            datetime.utcnow(),
            update_jobs_in_latest_wih_thread_task,
            interval=60*10,
        )

        scheduler.schedule(
            datetime.utcnow(),
            update_jobs_in_latest_fsf_thread_task,
            interval=60*10,
        )

        scheduler.schedule(
            datetime.utcnow(),
            update_jobs_in_latest_wwtbh_thread_task,
            interval=60*10,
        )
