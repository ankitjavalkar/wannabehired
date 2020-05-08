from django.shortcuts import render

def jobs(request):
	thread = Thread.objects.all().order_by('-created_on').first()
	jobs = job_list.jobs_set.all()
	return render(request, 'apps/scraper/list.html', {'jobs': jobs})
