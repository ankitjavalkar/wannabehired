import asyncio
from aiohttp import ClientSession
# import requests
import json



MASTER_USERNAME = 'whoishiring'
API_URL_MAP = {
    'post': 'https://hacker-news.firebaseio.com/v0/item/{}.json',
    'user': 'https://hacker-news.firebaseio.com/v0/user/{}.json',
}


class DeletedPostError(Exception):
   """Raised when the post is deleted"""
   pass


async def _get_response(resource_type, unique_id, session):
    url = API_URL_MAP.get(resource_type).format(unique_id)
    async with session.get(url) as response:
        reply = await response.read()
    response_as_dict = json.loads(reply)
    if response_as_dict.get('deleted', False):
        return None
    return response_as_dict

async def fetch_post_data_from_api(unique_id):
    async with ClientSession() as session:
        response_as_dict = await _get_response('post', unique_id, session)
    return response_as_dict

async def fetch_posts_data_from_api(unique_id_list):
    tasks = []
    async with ClientSession() as session:
        for _id in unique_id_list:
            task = asyncio.create_task(_get_response('post', _id, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses

async def fetch_user_data_from_api(username):
    async with ClientSession() as session:
        response_as_dict = await _get_response('user', username, session)
    return response_as_dict

async def fetch_comment_ids_from_api(unique_id):
    hn_thread_data = await fetch_post_data_from_api(unique_id)
    return hn_thread_data.get('kids', [])

async def fetch_thread_ids_from_api(username=MASTER_USERNAME):
    hn_user_data = await fetch_user_data_from_api(username)
    return hn_user_data.get('submitted', [])
