from neo4j import GraphDatabase
from flask import jsonify, current_app
import psycopg2
from auth import authenticate_user
from db_specs import db_config
import logging
from datetime import datetime

# Neo4j connection parameters
neo4j_uri = "bolt://neo4j:7687"
neo4j_user = "neo4j"
neo4j_password = "123456789"

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# PostgreSQL connection
def connect_to_postgres():
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except psycopg2.Error as e:
        current_app.logger.error("Error connecting to PostgreSQL: %s", e)
        return None

# Helper function to check and authenticate the user
def authenticate_request(request):
    token = request.cookies.get('token')
    
    if not token:
        token = request.get_json().get('token')
    
    if not token:
        return None, jsonify({'message': 'Unauthorized'}), 401
    
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return None, jsonify({'message': 'Unauthorized'}), 401
    
    return user_info, None, None


def create_post(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code
    
    user_id = int(user_info['id'])

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    images = data.get('images')
    created_at = data.get('created_at')
    status = "draft"

    with driver.session() as session:
        # Find the blog authored by the user
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:AUTHOR_OF]->(b:Blog)
            RETURN b.id AS blog_id
            """,
            user_id=user_id
        )

        blog = result.single()
        if not blog:
            return jsonify({'message': 'Blog not found for the user'}), 404

        blog_id = blog['blog_id']

        # Find the post with the largest ID and increment it by one
        result = session.run(
            """
            MATCH (p:Post)
            RETURN MAX(p.id) AS max_post_id
            """
        )

        max_post = result.single()
        max_post_id = max_post['max_post_id']
        post_id = (max_post_id + 1) if max_post_id is not None else 1

        # Create the post within the blog
        result = session.run(
            """
            MATCH (b:Blog {id: $blog_id})
            CREATE (b)-[:CONTAINS]->(p:Post {
                id: $post_id, title: $title, description: $description, created_at: $created_at, status: $status, images: $images
            })
            RETURN p;
            """,
            blog_id=blog_id, post_id=post_id, title=title, description=description, created_at=created_at, status=status, images=images
        )

        posts = [dict(record['p']) for record in result]
        current_app.logger.info("Results: %s", posts)

        if not posts:
            current_app.logger.error("No posts created in Neo4j.")

        return jsonify(posts), 201

def get_posts_by_blog(request, blog_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    try:
        blog_id = int(blog_id)  # Ensure the blog_id is an integer
    except ValueError:
        return jsonify({'message': 'Invalid blog ID'}), 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (b:Blog {id: $blog_id})-[:CONTAINS]->(p:Post)
            RETURN p;
            """,
            blog_id=blog_id
        )
        
        posts = [dict(record['p']) for record in result]
        if not posts:
            return jsonify({'message': 'No posts found for this blog'}), 404
        
        for post in posts:
            if 'created_at' in post:
                post['created_at'] = post['created_at'].isoformat()

        return jsonify(posts), 200

def get_all_posts(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Post)
            RETURN p;
            """
        )
        
        posts = [dict(record['p']) for record in result]
        
        # Convert DateTime objects to strings
        for post in posts:
            if 'created_at' in post:
                post['created_at'] = str(post['created_at'])
        
        
        return jsonify(posts), 200



def update_post(request, post_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    images = data.get('images')
    created_at = data.get('created_at')
    status = data.get('status')

    with driver.session() as session:
        # Check if the user is the author of the post
        result = session.run(
            """
            MATCH (p:Post {id: $post_id})<-[:CONTAINS]-(b:Blog)<-[:AUTHOR_OF]-(u:User {id: $user_id})
            RETURN p;
            """,
            post_id=int(post_id), user_id=user_id
        )
        
        post = result.single()
        if not post:
            return jsonify({'message': 'Unauthorized or Post not found'}), 401

        # Fetch the existing post
        result = session.run(
            """
            MATCH (p:Post {id: $post_id})
            RETURN p;
            """,
            post_id=int(post_id)
        )

        existing_post = result.single()
        if not existing_post:
            return jsonify({'message': 'Post not found'}), 404

        # Get the existing post properties
        post_properties = existing_post['p']

        # Use existing values if not provided in the request
        title = title if title is not None else post_properties['title']
        description = description if description is not None else post_properties['description']
        images = images if images is not None else post_properties['images']
        created_at = created_at if created_at is not None else post_properties['created_at']
        status = status if status is not None else post_properties['status']

        # Update the post with the new values
        result = session.run(
            """
            MATCH (p:Post {id: $post_id})
            SET p.title = $title, p.description = $description, p.images = $images, p.created_at = $created_at, p.status = $status
            RETURN p;
            """,
            post_id=int(post_id), title=title, description=description, images=images, created_at=created_at, status=status
        )

        updated_post = result.single()
        if not updated_post:
            return jsonify({'message': 'Failed to update post'}), 500

        updated_post = dict(updated_post['p'])
        if 'created_at' in updated_post:
            updated_post['created_at'] = str(updated_post['created_at'])

        return jsonify(updated_post), 200

def delete_post(request, post_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code
    
    user_id = int(user_info['id'])

    with driver.session() as session:
        # Check if the user is the author of the post
        result = session.run(
            """
            MATCH (p:Post {id: $post_id})<-[:CONTAINS]-(b:Blog)<-[:AUTHOR_OF]-(u:User {id: $user_id})
            RETURN p;
            """,
            post_id=int(post_id), user_id=user_id
        )
        
        post = result.single()
        if not post:
            return jsonify({'message': 'Unauthorized or Post not found'}), 401

        # Delete the post
        result = session.run(
            """
            MATCH (p:Post {id: $post_id})
            DETACH DELETE p;
            """,
            post_id=int(post_id)
        )
        
        summary = result.consume()
        if summary.counters.nodes_deleted == 0:
            return jsonify({'message': 'Post not found'}), 404
        
        return jsonify({'message': 'Post deleted successfully'}), 200
