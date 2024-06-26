from flask import jsonify, current_app
import psycopg2
from auth import authenticate_user
from db_specs import db_config
from saga_orchestrator import saga_orchestration_create_blog

def create_blog(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Check if the user has already created a blog
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM blogs WHERE user_id = %s", (user_id,))
        existing_blog = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if existing_blog:
            return jsonify({'message': 'You have already created a blog'}), 400
    except Exception as e:
        return jsonify({'message': 'Error checking existing blog', 'error': str(e)}), 500

    # Extract data from request
    title = request.json.get('title')
    description = request.json.get('description')

    if not all([title, description]):
        return jsonify({'message': 'Incomplete data provided'}), 400

    # Perform the blog creation
    return saga_orchestration_create_blog(user_id, title, description, token)

    
def create_post(request, blog_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    
    # Extract data from request
    title = request.json.get('title')
    description = request.json.get('description')
    date = request.json.get('date')
    images = request.json.get('images', [])
    status = request.json.get('status', 'draft')  # default to 'draft' if not provided

    if not all([title, description, date]):
        return jsonify({'message': 'Incomplete data provided'}), 400

    # Connect to PostgreSQL and insert the new post
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if the blog exists and belongs to the user
        cursor.execute("SELECT user_id FROM blogs WHERE id = %s", (blog_id,))
        blog_user_id = cursor.fetchone()
        if not blog_user_id or blog_user_id[0] != user_id:
            return jsonify({'message': 'Unauthorized: Blog does not exist or does not belong to the user'}), 401

        # Insert the new post into the blog
        cursor.execute("INSERT INTO posts (blog_id, title, description, images, status) VALUES (%s, %s, %s, %s, %s)", 
                       (blog_id, title, description, images, status))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Post created successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating post', 'error': str(e)}), 500
    
def post_comment(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    
    # Extract data from request
    post_id = request.json.get('post_id')
    comment_text = request.json.get('comment_text')

    if not all([post_id, comment_text]):
        return jsonify({'message': 'Incomplete data provided'}), 400

    # Connect to PostgreSQL and insert the new comment
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)", 
                       (post_id, user_id, comment_text))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Comment posted successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error posting comment', 'error': str(e)}), 500

    
    
# Function to handle editing comments
def edit_comment(request, comment_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Extract new comment text from request
    new_comment_text = request.json.get('comment_text')

    # Connect to PostgreSQL and update the comment
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE comments SET comment_text = %s, last_edited_at = CURRENT_TIMESTAMP WHERE id = %s AND user_id = %s", 
                       (new_comment_text, comment_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Comment edited successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error editing comment', 'error': str(e)}), 500
    
    
from datetime import datetime

# Function to handle getting all posts
def get_all_posts(request):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        posts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert each post entry to a dictionary with specific keys
        formatted_posts = []
        for post in posts:
            post_dict = {
                'id': post[0],
                'blog_id': post[1],
                'title': post[2],
                'description': post[3],
            }
            # Check if created_at field is a valid datetime object
            if isinstance(post[4], datetime):
                post_dict['created_at'] = post[4].strftime("%Y-%m-%d %H:%M:%S")
            else:
                post_dict['created_at'] = str(post[4])  # Handle case when created_at is not a datetime object
            formatted_posts.append(post_dict)
        
        return jsonify({'posts': formatted_posts}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving posts', 'error': str(e)}), 500



    
# Function to handle getting all blog posts
def get_all_blogs(request):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blogs")
        blogs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert each blog entry to a dictionary with specific keys
        formatted_blogs = []
        for blog in blogs:
            blog_dict = {
                'id': blog[0],
                'user_id': blog[1],
                'title': blog[2],
                'description': blog[3],
                'created_at': blog[4].strftime("%Y-%m-%d %H:%M:%S")
            }
            formatted_blogs.append(blog_dict)
        
        return jsonify({'blogs': formatted_blogs}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving blog posts', 'error': str(e)}), 500

# Function to handle getting a specific blog post by its ID
def get_blog_by_id(request, blog_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT b.id, b.user_id, b.title, b.description, b.created_at, u.Username FROM blogs b INNER JOIN users u ON b.user_id = u.ID WHERE b.id = %s", (blog_id,))
        blog = cursor.fetchone()
        cursor.close()
        conn.close()
        if blog:
            blog_dict = {
                'id': blog[0],
                'user_id': blog[1],
                'title': blog[2],
                'description': blog[3],
                'created_at': blog[4].strftime("%Y-%m-%d %H:%M:%S"),
                'author': blog[5]
            }
            return jsonify({'blog': blog_dict}), 200
        else:
            return jsonify({'message': 'Blog not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error retrieving blog', 'error': str(e)}), 500



# Function to handle getting a specific blog post by its ID
# Function to handle getting a specific post by its ID
# Function to handle getting a specific post by its ID
def get_post_by_id(request, post_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, blog_id, title, description, images, status, created_at FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        cursor.close()
        conn.close()
        if post:
            post_dict = {
                'id': post[0],
                'blog_id': post[1],
                'title': post[2],
                'description': post[3],
                'images': post[4],
                'status': post[5],
                'created_at': post[6].strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify({'post': post_dict}), 200
        else:
            return jsonify({'message': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error retrieving post', 'error': str(e)}), 500




# Function to handle getting all comments on a specific post
def get_comments_by_post_id(request, post_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT c.id, c.parent_comment_id, c.user_id, c.comment_text, c.likes, c.created_at, u.Username FROM comments c INNER JOIN users u ON c.user_id = u.ID WHERE c.post_id = %s ORDER BY c.id", (post_id,))
        comments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create a dictionary to store comments organized by their parent_comment_id
        comments_dict = {}
        for comment in comments:
            comment_id, parent_comment_id, user_id, comment_text, likes, created_at, username = comment
            if parent_comment_id is None:
                # If comment has no parent, add it directly to the dictionary
                comments_dict[comment_id] = {
                    'comment_id': comment_id,
                    'parent_comment_id': parent_comment_id,
                    'comment_text': comment_text,
                    'author': {'user_id': user_id, 'username': username},
                    'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'likes': likes,
                    'replies': []
                }
            else:
                # If comment has a parent, add it as a reply under the parent comment
                if parent_comment_id in comments_dict:
                    comments_dict[parent_comment_id]['replies'].append({
                        'comment_id': comment_id,
                        'parent_comment_id': parent_comment_id,
                        'comment_text': comment_text,
                        'author': {'user_id': user_id, 'username': username},
                        'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'likes': likes
                    })
        
        # Return the organized comments
        return jsonify({'comments': list(comments_dict.values())}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving comments for post', 'error': str(e)}), 500

def add_platform_review(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    
    # Extract data from request
    rating = request.json.get('rating')
    comment = request.json.get('comment')

    if rating is None or not (1 <= rating <= 5):
        return jsonify({'message': 'Invalid rating provided'}), 400

    # Connect to PostgreSQL and insert or update the platform review
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if the user already has a review
        cursor.execute("SELECT id FROM PlatformReview WHERE user_id = %s", (user_id,))
        existing_review = cursor.fetchone()

        if existing_review:
            # Update the existing review
            cursor.execute(
                "UPDATE PlatformReview SET rating = %s, comment = %s WHERE id = %s",
                (rating, comment, existing_review[0])
            )
        else:
            # Insert a new review
            cursor.execute(
                "INSERT INTO PlatformReview (user_id, rating, comment) VALUES (%s, %s, %s)", 
                (user_id, rating, comment)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Platform review submitted successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error adding platform review', 'error': str(e)}), 500


def get_platform_review(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Connect to PostgreSQL and fetch the platform review
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Fetch the review for the user
        cursor.execute("SELECT rating, comment FROM PlatformReview WHERE user_id = %s", (user_id,))
        review = cursor.fetchone()

        cursor.close()
        conn.close()

        if review:
            return jsonify({'rating': review[0], 'comment': review[1]}), 200
        else:
            return jsonify({'message': 'No review found for the user'}), 404
    except Exception as e:
        return jsonify({'message': 'Error fetching platform review', 'error': str(e)}), 500



def like_post(request, post_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Connect to PostgreSQL and insert the like for the post
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO post_likes (post_id, user_id) VALUES (%s, %s)", 
                       (post_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Post liked successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error liking post', 'error': str(e)}), 500


def cancel_post_like(request, post_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Connect to PostgreSQL and delete the user's like for the post
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM post_likes WHERE post_id = %s AND user_id = %s", 
                       (post_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Like canceled successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error canceling like', 'error': str(e)}), 500


def like_comment(request, comment_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Connect to PostgreSQL and insert the like for the comment
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comment_likes (comment_id, user_id) VALUES (%s, %s)", 
                       (comment_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Comment liked successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error liking comment', 'error': str(e)}), 500


def cancel_comment_like(request, comment_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Connect to PostgreSQL and delete the user's like for the comment
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comment_likes WHERE comment_id = %s AND user_id = %s", 
                       (comment_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Like canceled successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error canceling like', 'error': str(e)}), 500


def rate_blog(request, blog_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Extract data from request
    rating = request.json.get('rating')

    # Check if rating is valid
    if rating is None or not (1 <= rating <= 5):
        return jsonify({'message': 'Invalid rating provided'}), 400

    # Connect to PostgreSQL and insert/update the blog rating
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if a rating already exists for the user and blog
        cursor.execute("SELECT id FROM blog_ratings WHERE user_id = %s AND blog_id = %s", (user_id, blog_id))
        existing_rating = cursor.fetchone()

        if existing_rating:
            # Update existing rating
            cursor.execute("UPDATE blog_ratings SET rating = %s WHERE id = %s", (rating, existing_rating[0]))
        else:
            # Insert new rating
            cursor.execute("INSERT INTO blog_ratings (user_id, blog_id, rating) VALUES (%s, %s, %s)", (user_id, blog_id, rating))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Blog rated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error rating blog', 'error': str(e)}), 500
    
def get_user_blog(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Connect to PostgreSQL and retrieve the user's blog if it exists
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, created_at FROM blogs WHERE user_id = %s", (user_id,))
        user_blog = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_blog:
            blog_dict = {
                'id': user_blog[0],
                'title': user_blog[1],
                'description': user_blog[2],
                'created_at': user_blog[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(blog_dict), 200
        else:
            return jsonify({'message': 'You do not have a blog'}), 404
    except Exception as e:
        return jsonify({'message': 'Error retrieving user blog', 'error': str(e)}), 500

