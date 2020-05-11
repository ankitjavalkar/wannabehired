import requests
import datetime
import html

from django.db import models

from .utils import (API_URL_MAP, fetch_post_data_from_api,
    fetch_thread_ids_from_api, fetch_comment_ids_from_api, DeletedPostError
)

class Thread(models.Model):
    """
    Model to hold information about the monthly job list
    """

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    unique_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    @classmethod
    def map_data_to_object(cls, data):
        return Thread(
            title=data.get('title', ''),
            text=data.get('text', ''),
            unique_id=data.get("id"),
            timestamp=datetime.datetime.fromtimestamp(
                data.get("time", 0)
            )
        )

    @classmethod
    def fetch_new_thread_ids(cls):
        thread_ids = cls.objects.all().values_list('unique_id', flat=True)
        updated_thread_ids = fetch_thread_ids_from_api()
        new_thread_ids = [_id for _id in list(updated_thread_ids) if _id not in list(thread_ids)]
        return new_thread_ids

    @classmethod
    def fetch_thread(cls, unique_id):
        try:
            thread_data = fetch_post_data_from_api(unique_id)
            thread = Thread.map_data_to_object(thread_data)
        except DeletedPostError:
            return None
        return thread

    @classmethod
    def fetch_threads(cls, unique_ids):
        threads = []
        for thread_id in unique_ids:
            thread = Thread.fetch_thread(thread_id)
            if thread:
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

    @classmethod
    def fetch_job(cls, thread, unique_id):
        try:
            data = fetch_post_data_from_api(unique_id)
            job = Job.map_data_to_object(thread, data)
        except DeletedPostError:
            return None
        return job

    @classmethod
    def fetch_jobs(cls, thread, unique_ids):
        jobs = []
        for job_id in unique_ids:
            job = Thread.fetch_job(thread, job_id)
            if job:
                jobs.append(job)
            else:
                continue
        return jobs

    def fetch_new_job_ids(self):
        job_ids = self.job_set.all().values_list('unique_id', flat=True)
        updated_job_ids = fetch_comment_ids_from_api(self.unique_id)
        new_job_ids = [_id for _id in updated_job_ids if _id not in job_ids]
        return new_job_ids

    def fetch_new_jobs(self):
        new_job_ids = self.fetch_new_job_ids()
        new_jobs = Thread.fetch_jobs(self, new_job_ids)
        return new_jobs

    def update_new_jobs(self):
        new_jobs = self.fetch_new_jobs()
        Job.create_jobs(new_jobs)


class Job(models.Model):
    """
    Model to hold job post information 
    """

    created_on = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    # title = models.CharField(max_length=254)
    content = models.TextField()
    unique_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    @classmethod
    def map_data_to_object(cls, thread, data):
        return Job(
            thread=thread,
            # title=cls.get_title(data.get(text)),
            content=html.unescape(data.get('text')), # unescape the encoded HTML
            unique_id=data.get("id"),
            timestamp=datetime.datetime.fromtimestamp(
                data.get("time")
            )
        )

    # @classmethod
    # def get_title(cls, text):
    #     return text.split('<p>', 1)[0]

    # @classmethod
    # def get_content(cls, text):
    #     return text.split('<p>', 1)[1]

    @classmethod
    def create_jobs(cls, jobs):
        cls.objects.bulk_create(jobs)
