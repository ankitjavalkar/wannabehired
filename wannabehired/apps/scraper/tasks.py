from .models import *

def fetch_new_jobs_task():
    thread = Thread.objects.all().order_by('-timestamp').first()
    thread.update_new_jobs
