from django.shortcuts import render
from django.db.models import Q

from .models import Thread, Job
from .forms import SearchForm


def jobs(request):
    thread = Thread.objects.all().order_by('created_on').first()
    jobs = thread.job_set.all()
    search_form = SearchForm()
    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            thread_id = search_form.cleaned_data.pop('thread')
            query = Q(thread__id=thread_id)
            for field, val in search_form.cleaned_data.items():
                if val:
                    if field != 'keywords':
                            query &= Q(title__icontains=field)
                    else:
                        query &= (
                            Q(title__icontains=val) | Q(content__icontains=val)
                        )
            jobs = Job.objects.filter(query)
    return render(
        request,
        'scraper/list.html',
        {
            'jobs': jobs,
            'search_form': search_form,
        },
    )
