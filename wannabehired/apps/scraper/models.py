import asyncio
import datetime
import html

from django.db import models
from django.utils import timezone

from .utils import (API_URL_MAP, fetch_post_data_from_api,
    fetch_thread_ids_from_api, fetch_comment_ids_from_api, DeletedPostError,
    fetch_posts_data_from_api
)


class Thread(models.Model):
    """
    Model to hold information about the monthly job list
    """

    WIH_STRING = 'Who is hiring?'
    FSF_STRING = 'Freelancer? Seeking freelancer?'
    WWTBH_STRING = 'Who wants to be hired?'

    class ThreadType(models.TextChoices):
        WIH = 'wih', 'Who Is Hiring'
        FSF = 'fsf', 'Freelancer / Seeking Freelancer'
        WWTBH = 'wwtbh', 'Who Wants To Be Hired'

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    unique_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    thread_type = models.CharField(
        max_length=10,
        choices=ThreadType.choices,
        blank=True,
        null=True,
    )

    @classmethod
    def map_data_to_object(cls, data):
        return Thread(
            title=data.get('title', ''),
            text=data.get('text', ''),
            unique_id=data.get("id"),
            timestamp=datetime.datetime.fromtimestamp(
                data.get("time", 0), tz=timezone.utc
            ),
            thread_type=cls.get_type(data.get('title', ''))
        )

    @classmethod
    def get_type(cls, title):
        if cls.WIH_STRING in title:
            return cls.ThreadType.WIH
        elif cls.FSF_STRING in title:
            return cls.ThreadType.FSF
        elif cls.WWTBH_STRING in title:
            return cls.ThreadType.WWTBH
        return None

    @classmethod
    def fetch_new_thread_ids(cls):
        thread_ids = cls.objects.all().values_list('unique_id', flat=True)
        updated_thread_ids = asyncio.run(fetch_thread_ids_from_api())
        new_thread_ids = [_id for _id in list(updated_thread_ids) if str(_id) not in list(thread_ids)]
        return new_thread_ids

    @classmethod
    def fetch_thread(cls, unique_id):
        try:
            thread_data = asyncio.run(fetch_post_data_from_api(unique_id))
            if thread_data:
                thread = Thread.map_data_to_object(thread_data)
            else:
                return None
        except DeletedPostError:
            return None
        return thread

    @classmethod
    def fetch_threads(cls, unique_ids):
        threads = []
        data = asyncio.run(fetch_posts_data_from_api(unique_ids))
        for thread_data in data:
            if thread_data:
                thread = Thread.map_data_to_object(thread_data)
                threads.append(thread)
            else:
                continue
        return threads

    @classmethod
    def fetch_new_threads(cls):
        new_thread_ids = Thread.fetch_new_thread_ids()
        new_threads = Thread.fetch_threads(new_thread_ids)
        return new_threads

    @classmethod
    def update_new_threads(cls):
        threads = cls.fetch_new_threads()
        cls.objects.bulk_create(threads)
        return threads

    @classmethod
    def fetch_job(cls, thread, unique_id):
        try:
            data = asyncio.run(fetch_post_data_from_api(unique_id))
            if data:
                job = Job.map_data_to_object(thread, data)
            else:
                return None
        except DeletedPostError:
            return None
        return job

    @classmethod
    def fetch_jobs(cls, thread, unique_ids):
        jobs = []
        data = asyncio.run(fetch_posts_data_from_api(unique_ids))
        for job_data in data:
            if job_data:
                job = Job.map_data_to_object(thread, job_data)
                jobs.append(job)
            else:
                continue
        return jobs

    def fetch_new_job_ids(self):
        job_ids = self.job_set.all().values_list('unique_id', flat=True)
        updated_job_ids = asyncio.run(fetch_comment_ids_from_api(self.unique_id))
        new_job_ids = [_id for _id in updated_job_ids if _id not in job_ids]
        return new_job_ids

    def fetch_new_jobs(self):
        new_job_ids = self.fetch_new_job_ids()
        new_jobs = Thread.fetch_jobs(self, new_job_ids)
        return new_jobs

    def update_new_jobs(self):
        new_jobs = self.fetch_new_jobs()
        Job.create_jobs(new_jobs)

    def __str__(self):
        thread_type = self.get_thread_type_display()
        readable_time = self.timestamp.strftime("%d-%m-%Y")
        return "{} | {}".format(thread_type, readable_time)

class Job(models.Model):
    """
    Model to hold job post information 
    """

    created_on = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    title = models.CharField(max_length=254)
    content = models.TextField()
    unique_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    @classmethod
    def map_data_to_object(cls, thread, data):
        title = cls.get_title_and_content(data.get("text"))[0]
        content = cls.get_title_and_content(data.get("text"))[1]
        return Job(
            thread=thread,
            title=title,
            content=html.unescape(content), # unescape the encoded HTML
            unique_id=data.get("id"),
            timestamp=datetime.datetime.fromtimestamp(
                data.get("time"), tz=timezone.utc
            )
        )

    @classmethod
    def get_title_and_content(cls, text):
        text_split = text.split('<p>', 1)
        if not len(text_split) > 1:
            return '', text_split[0]
        return text_split

    @classmethod
    def create_jobs(cls, jobs):
        cls.objects.bulk_create(jobs)

    def __str__(self):
        return "{} | {}".format(self.thread, self.title[:50])
