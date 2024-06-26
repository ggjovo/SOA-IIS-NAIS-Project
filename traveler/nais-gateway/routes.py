from flask import Blueprint

from blog_service_adapter import (
    create_blog_route, create_post_route, get_user_blog_route,
    post_comment_route, edit_comment_route, get_all_blog_posts, get_all_blogs_route,
    get_blog_by_id_route, get_post_by_id_route, get_comments_for_post_route,
    add_platform_review_route, get_platform_review_route, like_post_route,
    like_comment_route, cancel_like_post_route, cancel_like_comment_route,
    rate_blog_route, user_follow, user_unfollow, block_user_route,
    get_platform_reviews_route, get_average_rating_by_day_route
)

from blog_recommender_adapter import (
    get_recommended_posts, create_new_blog, get_blog,
    update_existing_blog, delete_existing_blog, get_all_blog_posts,
    create_new_post, get_posts_for_blog, get_all_posts_route,
    update_existing_post, delete_existing_post, create_new_comment,
    get_comment, update_existing_comment, delete_existing_comment,
    get_all_comments_route, get_comments_for_post, like_comment_route,
    create_new_user, get_user, update_existing_user,
    delete_existing_user, get_all_users_route, rate_blog_route
)

gateway_routes = Blueprint('gateway', __name__)

# Blog Service Routes
@gateway_routes.route('/blog_service/blog', methods=['POST'])
def create_blog():
    return create_blog_route()

@gateway_routes.route('/blog_service/post/<int:blog_id>', methods=['POST'])
def create_post(blog_id):
    return create_post_route(blog_id)

@gateway_routes.route('/blog_service/get_user_blog', methods=['GET'])
def get_user_blog():
    return get_user_blog_route()

@gateway_routes.route('/blog_service/comment', methods=['POST'])
def post_comment():
    return post_comment_route()

@gateway_routes.route('/blog_service/comment/<int:comment_id>', methods=['PUT'])
def edit_comment(comment_id):
    return edit_comment_route(comment_id)

@gateway_routes.route('/blog_service/posts', methods=['GET'])
def get_all_blog_posts_r():
    return get_all_blog_posts()

@gateway_routes.route('/blog_service/blogs', methods=['GET'])
def get_all_blogs():
    return get_all_blogs_route()

@gateway_routes.route('/blog_service/blog/<int:blog_id>', methods=['GET'])
def get_blog_by_id(blog_id):
    return get_blog_by_id_route(blog_id)

@gateway_routes.route('/blog_service/post/<int:post_id>', methods=['GET'])
def get_post_by_id(post_id):
    return get_post_by_id_route(post_id)

@gateway_routes.route('/blog_service/post/<int:post_id>/comments', methods=['GET'])
def get_comments_for_post(post_id):
    return get_comments_for_post_route(post_id)

@gateway_routes.route('/blog_service/platform_review', methods=['POST'])
def add_platform_review():
    return add_platform_review_route()

@gateway_routes.route('/blog_service/get_review', methods=['GET'])
def get_platform_review():
    return get_platform_review_route()

@gateway_routes.route('/blog_service/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    return like_post_route(post_id)

@gateway_routes.route('/blog_service/like_comment/<int:comment_id>', methods=['POST'])
def like_comment(comment_id):
    return like_comment_route(comment_id)

@gateway_routes.route('/blog_service/like_post/<int:post_id>', methods=['DELETE'])
def cancel_like_post(post_id):
    return cancel_like_post_route(post_id)

@gateway_routes.route('/blog_service/like_comment/<int:comment_id>', methods=['DELETE'])
def cancel_like_comment(comment_id):
    return cancel_like_comment_route(comment_id)

@gateway_routes.route('/blog_service/blog/<int:blog_id>/rate', methods=['POST'])
def rate_blog(blog_id):
    return rate_blog_route(blog_id)

@gateway_routes.route('/blog_service/follow', methods=['POST'])
def user_follow_route():
    return user_follow()

@gateway_routes.route('/blog_service/unfollow', methods=['POST'])
def user_unfollow_route():
    return user_unfollow()

@gateway_routes.route('/blog_service/admin/block_user/<int:user_id_to_block>', methods=['PUT'])
def block_user(user_id_to_block):
    return block_user_route(user_id_to_block)

@gateway_routes.route('/blog_service/admin/platform_reviews', methods=['GET'])
def get_platform_reviews():
    return get_platform_reviews_route()

@gateway_routes.route('/blog_service/admin/average_rating_by_day', methods=['GET'])
def get_average_rating_by_day():
    return get_average_rating_by_day_route()

# Blog Recommender Routes
@gateway_routes.route('/blog_recommender/recommend', methods=['GET'])
def recommend():
    return get_recommended_posts()

@gateway_routes.route('/blog_recommender/blogs', methods=['POST'])
def new_blog():
    return create_new_blog()

@gateway_routes.route('/blog_recommender/blogs/<blog_id>', methods=['GET'])
def read_blog(blog_id):
    return get_blog(blog_id)

@gateway_routes.route('/blog_recommender/blogs/<blog_id>', methods=['PUT'])
def update_blog(blog_id):
    return update_existing_blog(blog_id)

@gateway_routes.route('/blog_recommender/blogs/<blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    return delete_existing_blog(blog_id)

@gateway_routes.route('/blog_recommender/blogs', methods=['GET'])
def get_all_blogs_recommender():
    return get_all_blog_posts()

@gateway_routes.route('/blog_recommender/posts', methods=['POST'])
def new_post():
    return create_new_post()

@gateway_routes.route('/blog_recommender/blogs/<blog_id>/posts', methods=['GET'])
def posts_for_blog(blog_id):
    return get_posts_for_blog(blog_id)

@gateway_routes.route('/blog_recommender/posts', methods=['GET'])
def all_posts():
    return get_all_posts_route()

@gateway_routes.route('/blog_recommender/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    return update_existing_post(post_id)

@gateway_routes.route('/blog_recommender/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    return delete_existing_post(post_id)

@gateway_routes.route('/blog_recommender/comments', methods=['POST'])
def new_comment():
    return create_new_comment()

@gateway_routes.route('/blog_recommender/comments/<comment_id>', methods=['GET'])
def read_comment(comment_id):
    return get_comment(comment_id)

@gateway_routes.route('/blog_recommender/comments/<comment_id>', methods=['PUT'])
def update_comment(comment_id):
    return update_existing_comment(comment_id)

@gateway_routes.route('/blog_recommender/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    return delete_existing_comment(comment_id)

@gateway_routes.route('/blog_recommender/comments', methods=['GET'])
def all_comments():
    return get_all_comments_route()

@gateway_routes.route('/blog_recommender/posts/<post_id>/comments', methods=['GET'])
def comments_for_post(post_id):
    return get_comments_for_post(post_id)

@gateway_routes.route('/blog_recommender/comments/<comment_id>/like', methods=['POST'])
def like_comment_recommender(comment_id):
    return like_comment_route(comment_id)

@gateway_routes.route('/blog_recommender/users', methods=['POST'])
def new_user():
    return create_new_user()

@gateway_routes.route('/blog_recommender/users/<user_id>', methods=['GET'])
def read_user(user_id):
    return get_user(user_id)

@gateway_routes.route('/blog_recommender/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    return update_existing_user(user_id)

@gateway_routes.route('/blog_recommender/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    return delete_existing_user(user_id)

@gateway_routes.route('/blog_recommender/users', methods=['GET'])
def all_users():
    return get_all_users_route()

@gateway_routes.route('/blog_recommender/blogs/<blog_id>/rate', methods=['POST'])
def rate_blog_recommender(blog_id):
    return rate_blog_route(blog_id)
