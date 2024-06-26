import requests
from flask import request

BLOG_RECOMMENDER_URL = "http://blog_recommender:8085"

def forward_to_blog_recommender(endpoint, method='GET', data=None, headers=None):
    url = f"{BLOG_RECOMMENDER_URL}/{endpoint}"
    response = requests.request(method, url, json=data, headers=headers)
    return response.json(), response.status_code

def get_recommended_posts():
    return forward_to_blog_recommender('recommend', 'GET', request.json, request.headers)

def create_new_blog():
    return forward_to_blog_recommender('blogs', 'POST', request.json, request.headers)

def get_blog(blog_id):
    return forward_to_blog_recommender(f'blogs/{blog_id}', 'GET', request.json, request.headers)

def update_existing_blog(blog_id):
    return forward_to_blog_recommender(f'blogs/{blog_id}', 'PUT', request.json, request.headers)

def delete_existing_blog(blog_id):
    return forward_to_blog_recommender(f'blogs/{blog_id}', 'DELETE', request.json, request.headers)

def get_all_blog_posts():
    return forward_to_blog_recommender('blogs', 'GET', request.json, request.headers)

def create_new_post():
    return forward_to_blog_recommender('posts', 'POST', request.json, request.headers)

def get_posts_for_blog(blog_id):
    return forward_to_blog_recommender(f'blogs/{blog_id}/posts', 'GET', request.json, request.headers)

def get_all_posts_route():
    return forward_to_blog_recommender('posts', 'GET', request.json, request.headers)

def update_existing_post(post_id):
    return forward_to_blog_recommender(f'posts/{post_id}', 'PUT', request.json, request.headers)

def delete_existing_post(post_id):
    return forward_to_blog_recommender(f'posts/{post_id}', 'DELETE', request.json, request.headers)

def create_new_comment():
    return forward_to_blog_recommender('comments', 'POST', request.json, request.headers)

def get_comment(comment_id):
    return forward_to_blog_recommender(f'comments/{comment_id}', 'GET', request.json, request.headers)

def update_existing_comment(comment_id):
    return forward_to_blog_recommender(f'comments/{comment_id}', 'PUT', request.json, request.headers)

def delete_existing_comment(comment_id):
    return forward_to_blog_recommender(f'comments/{comment_id}', 'DELETE', request.json, request.headers)

def get_all_comments_route():
    return forward_to_blog_recommender('comments', 'GET', request.json, request.headers)

def get_comments_for_post(post_id):
    return forward_to_blog_recommender(f'posts/{post_id}/comments', 'GET', request.json, request.headers)

def like_comment_route(comment_id):
    return forward_to_blog_recommender(f'comments/{comment_id}/like', 'POST', request.json, request.headers)

def create_new_user():
    return forward_to_blog_recommender('users', 'POST', request.json, request.headers)

def get_user(user_id):
    return forward_to_blog_recommender(f'users/{user_id}', 'GET', request.json, request.headers)

def update_existing_user(user_id):
    return forward_to_blog_recommender(f'users/{user_id}', 'PUT', request.json, request.headers)

def delete_existing_user(user_id):
    return forward_to_blog_recommender(f'users/{user_id}', 'DELETE', request.json, request.headers)

def get_all_users_route():
    return forward_to_blog_recommender('users', 'GET', request.json, request.headers)

def rate_blog_route(blog_id):
    return forward_to_blog_recommender(f'blogs/{blog_id}/rate', 'POST', request.json, request.headers)
