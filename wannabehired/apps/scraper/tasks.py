from datetime import datetime

import django_rq

from .models import *

def update_new_threads_task():
    threads = Thread.update_new_threads()

    thread_ids = [thread.unique_id for thread in threads]
    for thread_id in thread_ids:
        django_rq.enqueue(update_jobs_task, thread_id)

def update_jobs_task(thread_id):
    thread = Thread.objects.get(unique_id=thread_id)
    thread.update_new_jobs()

def update_jobs_in_latest_wih_thread_task():
    thread = Thread.objects.filter(
        thread_type='wih',
    ).latest('timestamp')
    thread.update_new_jobs()

def update_jobs_in_latest_fsf_thread_task():
    thread = Thread.objects.filter(
        thread_type='fsf',
    ).latest('timestamp')
    thread.update_new_jobs()

def update_jobs_in_latest_wwtbh_thread_task():
    thread = Thread.objects.filter(
        thread_type='wwtbh',
    ).latest('timestamp')
    thread.update_new_jobs()
