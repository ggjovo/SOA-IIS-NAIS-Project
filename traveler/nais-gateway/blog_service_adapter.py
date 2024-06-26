import requests
from flask import request
import sys
import logging

BLOG_SERVICE_URL = "http://blog-microservice:8083"


logger = logging.getLogger(__name__)

def forward_to_blog_service(endpoint, method='GET', data=None, headers=None):
    url = f"{BLOG_SERVICE_URL}/{endpoint}"
    logger.info(f"Forwarding request to: {url}")
    logger.info(f"Request method: {method}")
    logger.info(f"Request data: {data}")
    logger.info(f"Request headers: {headers}")
    
    response = requests.request(method, url, json=data, headers=headers)
    
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response content: {response.content}")
    
    return response.json(), response.status_code, data

def create_blog_route():
    return forward_to_blog_service('blog', 'POST', request.json, request.headers)

def create_post_route(blog_id):
    return forward_to_blog_service(f'post/{blog_id}', 'POST', request.json, request.headers)

def get_user_blog_route():
    return forward_to_blog_service('get_user_blog', 'GET', request.json, request.headers)

def post_comment_route():
    return forward_to_blog_service('comment', 'POST', request.json, request.headers)

def edit_comment_route(comment_id):
    return forward_to_blog_service(f'comment/{comment_id}', 'PUT', request.json, request.headers)

def get_all_blog_posts():
    return forward_to_blog_service('posts', 'GET', request.json, request.headers)

def get_all_blogs_route():
    return forward_to_blog_service('blogs', 'GET', request.json, request.headers)

def get_blog_by_id_route(blog_id):
    return forward_to_blog_service(f'blog/{blog_id}', 'GET', request.json, request.headers)

def get_post_by_id_route(post_id):
    return forward_to_blog_service(f'post/{post_id}', 'GET', request.json, request.headers)

def get_comments_for_post_route(post_id):
    return forward_to_blog_service(f'post/{post_id}/comments', 'GET', request.json, request.headers)

def add_platform_review_route():
    return forward_to_blog_service('platform_review', 'POST', request.json, request.headers)

def get_platform_review_route():
    return forward_to_blog_service('get_review', 'GET', request.json, request.headers)

def like_post_route(post_id):
    return forward_to_blog_service(f'like_post/{post_id}', 'POST', request.json, request.headers)

def like_comment_route(comment_id):
    return forward_to_blog_service(f'like_comment/{comment_id}', 'POST', request.json, request.headers)

def cancel_like_post_route(post_id):
    return forward_to_blog_service(f'like_post/{post_id}', 'DELETE', request.json, request.headers)

def cancel_like_comment_route(comment_id):
    return forward_to_blog_service(f'like_comment/{comment_id}', 'DELETE', request.json, request.headers)

def rate_blog_route(blog_id):
    return forward_to_blog_service(f'blog/{blog_id}/rate', 'POST', request.json, request.headers)

def user_follow():
    return forward_to_blog_service('follow', 'POST', request.json, request.headers)

def user_unfollow():
    return forward_to_blog_service('unfollow', 'POST', request.json, request.headers)

def block_user_route(user_id_to_block):
    return forward_to_blog_service(f'admin/block_user/{user_id_to_block}', 'PUT', request.json, request.headers)

def get_platform_reviews_route():
    return forward_to_blog_service('admin/platform_reviews', 'GET', request.json, request.headers)

def get_average_rating_by_day_route():
    return forward_to_blog_service('admin/average_rating_by_day', 'GET', request.json, request.headers)
