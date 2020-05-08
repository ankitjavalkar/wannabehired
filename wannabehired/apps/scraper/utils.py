import requests
import json


MASTER_USERNAME = 'whoishiring'
API_URL_MAP = {
    'post': 'https://hacker-news.firebaseio.com/v0/item/{}.json',
    'user': 'https://hacker-news.firebaseio.com/v0/user/{}.json',
}


class DeletedPostError(Exception):
   """Raised when the post is deleted"""
   pass


def _get_response(resource_type, unique_id):
    url = API_URL_MAP.get(resource_type).format(unique_id)
    response = requests.get(url)
    return response.text   

def fetch_post_data_from_api(unique_id):
    response = _get_response('post', unique_id)
    response_as_dict = json.loads(response)
    if response_as_dict.get('deleted', False):
        raise DeletedPostError
    return response_as_dict

def fetch_user_data_from_api(username):
    response = _get_response('user', username)
    return json.loads(response)

def fetch_comment_ids_from_api(unique_id):
    hn_thread_data = fetch_post_data_from_api(unique_id)
    return hn_thread_data.get('kids', [])

def fetch_thread_ids_from_api(username=MASTER_USERNAME):
    hn_user_data = fetch_user_data_from_api(username)
    return hn_user_data.get('submitted', [])
