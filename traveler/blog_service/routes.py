from flask import Blueprint
from flask import request, jsonify
import requests
from auth import authenticate_user
from blog import (
    post_comment, edit_comment, get_all_posts, get_blog_by_id,
    create_blog, create_post, get_all_blogs, get_post_by_id, get_comments_by_post_id,
    add_platform_review, like_post, like_comment, cancel_comment_like, cancel_post_like, rate_blog, get_platform_review,
    get_user_blog
)
from following import follow_user, unfollow_user
from blog_admin import block_user, get_platform_reviews, get_average_rating_by_day

blog_routes = Blueprint('blog', __name__)

# Route to handle creating new blogs
@blog_routes.route('/blog', methods=['POST'])
def create_blog_route():
    return create_blog(request)

# Route to handle posting new blog posts
@blog_routes.route('/post/<int:blog_id>', methods=['POST'])
def create_post_route(blog_id):
    return create_post(request, blog_id)

@blog_routes.route('/get_user_blog', methods=['GET'])
def get_user_blog_route():
    return get_user_blog(request)

# Route to handle posting comments on blog posts
@blog_routes.route('/comment', methods=['POST'])
def post_comment_route():
    return post_comment(request)

# Route to handle editing comments
@blog_routes.route('/comment/<int:comment_id>', methods=['PUT'])
def edit_comment_route(comment_id):
    return edit_comment(request, comment_id)

# Route for getting all blog posts
@blog_routes.route('/posts', methods=['GET'])
def get_all_blog_posts():
    return get_all_posts(request)

# Route for getting all blogs
@blog_routes.route('/blogs', methods=['GET'])
def get_all_blogs_route():
    return get_all_blogs(request)

# Route for getting a specific blog by its ID
@blog_routes.route('/blog/<int:blog_id>', methods=['GET'])
def get_blog_by_id_route(blog_id):
    return get_blog_by_id(request, blog_id)

# Route for getting a specific post by its ID
@blog_routes.route('/post/<int:post_id>', methods=['GET'])
def get_post_by_id_route(post_id):
    return get_post_by_id(request, post_id)

# Route for getting comments on a specific post
@blog_routes.route('/post/<int:post_id>/comments', methods=['GET'])
def get_comments_for_post_route(post_id):
    return get_comments_by_post_id(request, post_id)

# Route to handle adding platform reviews
@blog_routes.route('/platform_review', methods=['POST'])
def add_platform_review_route():
    return add_platform_review(request)

# Route to handle adding platform reviews
@blog_routes.route('/get_review', methods=['GET'])
def get_platform_review_route():
    return get_platform_review(request)

# Route to handle liking a post
@blog_routes.route('/like_post/<int:post_id>', methods=['POST'])
def like_post_route(post_id):
    return like_post(request, post_id)

# Route to handle liking a comment
@blog_routes.route('/like_comment/<int:comment_id>', methods=['POST'])
def like_comment_route(comment_id):
    return like_comment(request, comment_id)

# Route to cancel a like on a post
@blog_routes.route('/like_post/<int:post_id>', methods=['DELETE'])
def cancel_like_post_route(post_id):
    return cancel_post_like(request, post_id)

# Route to cancel a like on a comment
@blog_routes.route('/like_comment/<int:comment_id>', methods=['DELETE'])
def cancel_like_comment_route(comment_id):
    return cancel_comment_like(request, comment_id)

# Route to handle rating a blog
@blog_routes.route('/blog/<int:blog_id>/rate', methods=['POST'])
def rate_blog_route(blog_id):
    return rate_blog(request, blog_id)

@blog_routes.route('/follow', methods=['POST'])
def user_follow():
    return follow_user(request)

@blog_routes.route('/unfollow', methods=['POST'])
def user_unfollow():
    return unfollow_user(request)

# Route to handle blocking a user by admin
@blog_routes.route('/admin/block_user/<int:user_id_to_block>', methods=['PUT'])
def block_user_route(user_id_to_block):
    return block_user(request, user_id_to_block)

# Route to handle getting platform reviews by admin
@blog_routes.route('/admin/platform_reviews', methods=['GET'])
def get_platform_reviews_route():
    return get_platform_reviews(request)

# Route to handle getting average rating by day
@blog_routes.route('/admin/average_rating_by_day', methods=['GET'])
def get_average_rating_by_day_route():
    return get_average_rating_by_day(request)


# Register the following blueprint
#blog_routes.register_blueprint(following_routes, url_prefix='/following')

# In your main app file, ensure you register the blueprint like so:
#app.register_blueprint(blog_routes, url_prefix='/api')
