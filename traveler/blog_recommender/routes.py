from flask import Blueprint, request, jsonify
from recommender import get_posts_for_user, get_most_popular_blogs, get_most_popular_posts, get_most_liked_blog_from_user, get_most_liked_blog_from_user_follows, get_simular_blogs_from_user_likes, get_simular_post_from_user_likes, get_simular_blog_from_user_follows, get_simular_posts_from_user_follows, get_simular_users_from_user_follows, get_most_active_user, get_most_popular_tags, get_best_rated_blogs
from crud.blogs import create_blog, delete_blog, get_all_blogs, update_blog, read_blog
from crud.posts import create_post, get_posts_by_blog, get_all_posts, update_post, delete_post
from crud.comments import create_comment, read_comment, update_comment, delete_comment, get_all_comments, get_comments_by_post, like_comment
from crud.users import create_user, read_user, update_user, delete_user, get_all_users, rate_blog

# Define the Blueprint
recommender_routes = Blueprint('neo4j', __name__)

# Existing routes for blogs
# Route to handle getting recommended posts
@recommender_routes.route('/recommend', methods=['GET'])
def get_recommended_posts():
    return get_posts_for_user(request)

# Route to handle creating new blogs
@recommender_routes.route('/blogs', methods=['POST'])
def create_new_blog():
    return create_blog(request)

# Route to handle reading a blog by ID
@recommender_routes.route('/blogs/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    return read_blog(request, blog_id)

# Route to handle updating a blog by ID
@recommender_routes.route('/blogs/<blog_id>', methods=['PUT'])
def update_existing_blog(blog_id):
    return update_blog(request, blog_id)

# Route to handle deleting a blog by ID
@recommender_routes.route('/blogs/<blog_id>', methods=['DELETE'])
def delete_existing_blog(blog_id):
    return delete_blog(request, blog_id)

# Route to handle getting all blogs
@recommender_routes.route('/blogs', methods=['GET'])
def get_all_blog_posts():
    return get_all_blogs(request)

# New routes for posts
# Route to handle creating new posts
@recommender_routes.route('/posts', methods=['POST'])
def create_new_post():
    return create_post(request)

# Route to handle getting posts for a specific blog
@recommender_routes.route('/blogs/<blog_id>/posts', methods=['GET'])
def get_posts_for_blog(blog_id):
    return get_posts_by_blog(request, blog_id)

# Route to handle getting all posts
@recommender_routes.route('/posts', methods=['GET'])
def get_all_posts_route():
    return get_all_posts(request)

# Route to handle updating a post by ID
@recommender_routes.route('/posts/<post_id>', methods=['PUT'])
def update_existing_post(post_id):
    return update_post(request, post_id)

# Route to handle deleting a post by ID
@recommender_routes.route('/posts/<post_id>', methods=['DELETE'])
def delete_existing_post(post_id):
    return delete_post(request, post_id)

# Routes for comments
# Route to handle creating a new comment
@recommender_routes.route('/comments', methods=['POST'])
def create_new_comment():
    return create_comment(request)

# Route to handle reading a comment by ID
@recommender_routes.route('/comments/<comment_id>', methods=['GET'])
def get_comment(comment_id):
    return read_comment(request, comment_id)

# Route to handle updating a comment by ID
@recommender_routes.route('/comments/<comment_id>', methods=['PUT'])
def update_existing_comment(comment_id):
    return update_comment(request, comment_id)

# Route to handle deleting a comment by ID
@recommender_routes.route('/comments/<comment_id>', methods=['DELETE'])
def delete_existing_comment(comment_id):
    return delete_comment(request, comment_id)

# Route to handle getting all comments
@recommender_routes.route('/comments', methods=['GET'])
def get_all_comments_route():
    return get_all_comments(request)

# Route to handle getting comments for a specific post
@recommender_routes.route('/posts/<post_id>/comments', methods=['GET'])
def get_comments_for_post(post_id):
    return get_comments_by_post(request, post_id)

# Route to handle liking a comment
@recommender_routes.route('/comments/<comment_id>/like', methods=['POST'])
def like_comment_route(comment_id):
    return like_comment(request, comment_id)

# Routes for users
# Route to handle creating a new user
@recommender_routes.route('/users', methods=['POST'])
def create_new_user():
    return create_user(request)

# Route to handle reading a user by ID
@recommender_routes.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    return read_user(request, user_id)

# Route to handle updating a user by ID
@recommender_routes.route('/users/<user_id>', methods=['PUT'])
def update_existing_user(user_id):
    return update_user(request, user_id)

# Route to handle deleting a user by ID
@recommender_routes.route('/users/<user_id>', methods=['DELETE'])
def delete_existing_user(user_id):
    return delete_user(request, user_id)

# Route to handle getting all users
@recommender_routes.route('/users', methods=['GET'])
def get_all_users_route():
    return get_all_users(request)

# Route to handle rating a blog
@recommender_routes.route('/blogs/<blog_id>/rate', methods=['POST'])
def rate_blog_route(blog_id):
    return rate_blog(request, blog_id)

@recommender_routes.route('/get_most_popular_blogs', methods=['GET'])
def get_most_popular_blogs_route():
    return get_most_popular_blogs()

@recommender_routes.route('/get_most_popular_posts', methods=['GET'])
def get_most_popular_posts_route():
    return get_most_popular_posts()

@recommender_routes.route('/get_most_liked_blog_from_user/<int:user_id>', methods=['GET'])
def get_most_liked_blog_from_user_route(user_id):
    return get_most_liked_blog_from_user(user_id)

@recommender_routes.route('/get_most_liked_blog_from_user_follows/<int:user_id>', methods=['GET'])
def get_most_liked_blog_from_user_follows_route(user_id):
    return get_most_liked_blog_from_user_follows(user_id)

@recommender_routes.route('/get_simular_blogs_from_user_likes/<int:user_id>', methods=['GET'])
def get_simular_blogs_from_user_likes_route(user_id):
    return get_simular_blogs_from_user_likes(user_id)

@recommender_routes.route('/get_simular_post_from_user_likes/<int:user_id>', methods=['GET'])
def get_simular_post_from_user_likes_route(user_id):
    return get_simular_post_from_user_likes(user_id)

@recommender_routes.route('/get_simular_blog_from_user_follows/<int:user_id>', methods=['GET'])
def get_simular_blog_from_user_follows_routes(user_id):
    return get_simular_blog_from_user_follows(user_id)

@recommender_routes.route('/get_simular_posts_from_user_follows/<int:user_id>', methods=['GET'])
def get_simular_posts_from_user_follows_route(user_id):
    return get_simular_posts_from_user_follows(user_id)

@recommender_routes.route('/get_simular_users_from_user_follows/<int:user_id>', methods=['GET'])
def get_simular_users_from_user_follows_route(user_id):
    return get_simular_users_from_user_follows(user_id)

@recommender_routes.route('/get_most_active_user', methods=['GET'])
def get_most_active_user_route():
    return get_most_active_user()

@recommender_routes.route('/get_best_rated_blogs', methods=['GET'])
def get_best_rated_blogs_route():
    return get_best_rated_blogs()

@recommender_routes.route('/get_most_popular_tags', methods=['GET'])
def get_most_popular_tags_route():
    return get_most_popular_tags()

