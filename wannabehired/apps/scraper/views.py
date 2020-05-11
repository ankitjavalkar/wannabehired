from django.shortcuts import render

from .models import Thread, Job

def jobs(request):
    thread = Thread.objects.all().order_by('created_on').first()
    jobs = thread.job_set.all()
    return render(request, 'scraper/list.html', {'jobs': jobs})
