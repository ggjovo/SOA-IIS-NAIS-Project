from neo4j import GraphDatabase
from flask import jsonify, current_app
import psycopg2
from auth import authenticate_user
from db_specs import db_config
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

def create_comment(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])
    data = request.get_json()
    post_id = data.get('post_id')
    parent_comment_id = data.get('parent_comment_id')
    comment_text = data.get('comment_text')
    created_at = data.get('created_at', str(datetime.utcnow()))
    last_edited_at = data.get('last_edited_at', created_at)
    likes = data.get('likes', 0)
    comment_id = int(data.get('comment_id'))  # Make sure the key is 'comment_id'

    with driver.session() as session:
        # Create the comment and associate it with the user and the post (or parent comment if it is a reply)
        if parent_comment_id:
            session.run(
                """
                MATCH (u:User {id: $user_id}), (parent:Comment {id: $parent_comment_id})
                CREATE (u)-[:AUTHOR_OF]->(c:Comment {
                    id: $comment_id, comment_text: $comment_text, created_at: $created_at, last_edited_at: $last_edited_at, likes: $likes
                })
                CREATE (parent)-[:REPLY_TO]->(c)
                RETURN c;
                """,
                user_id=user_id, parent_comment_id=parent_comment_id, comment_id=comment_id, comment_text=comment_text, created_at=created_at, last_edited_at=last_edited_at, likes=likes
            )
        else:
            session.run(
                """
                MATCH (u:User {id: $user_id}), (p:Post {id: $post_id})
                CREATE (u)-[:AUTHOR_OF]->(c:Comment {
                    id: $comment_id, comment_text: $comment_text, created_at: $created_at, last_edited_at: $last_edited_at, likes: $likes
                })
                CREATE (p)-[:HAS_COMMENT]->(c)
                RETURN c;
                """,
                user_id=user_id, post_id=post_id, comment_id=comment_id, comment_text=comment_text, created_at=created_at, last_edited_at=last_edited_at, likes=likes
            )

        return jsonify({'message': 'Comment created successfully'}), 201


def read_comment(request, comment_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    try:
        comment_id = int(comment_id)  # Ensure the comment_id is an integer
    except ValueError:
        return jsonify({'message': 'Invalid comment ID'}), 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Comment {id: $comment_id})
            RETURN c;
            """,
            comment_id=comment_id
        )
        
        comments = [dict(record['c']) for record in result]
        if not comments:
            return jsonify({'message': 'Comment not found'}), 404
        
        return jsonify(comments), 200


def update_comment(request, comment_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    data = request.get_json()
    comment_text = data.get('comment_text')
    last_edited_at = str(datetime.utcnow())

    with driver.session() as session:
        # Fetch the existing comment
        result = session.run(
            """
            MATCH (c:Comment {id: $comment_id})
            RETURN c;
            """,
            comment_id=int(comment_id)
        )

        existing_comment = result.single()
        if not existing_comment:
            return jsonify({'message': 'Comment not found'}), 404

        # Get the existing comment properties
        comment_properties = existing_comment['c']

        # Use existing values if not provided in the request
        comment_text = comment_text if comment_text is not None else comment_properties['comment_text']

        # Update the comment with the new values
        result = session.run(
            """
            MATCH (c:Comment {id: $comment_id})
            SET c.comment_text = $comment_text, c.last_edited_at = $last_edited_at
            RETURN c;
            """,
            comment_id=int(comment_id), comment_text=comment_text, last_edited_at=last_edited_at
        )

        updated_comment = result.single()
        if not updated_comment:
            return jsonify({'message': 'Failed to update comment'}), 500

        return jsonify(dict(updated_comment['c'])), 200


def delete_comment(request, comment_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])

    with driver.session() as session:
        # Check if the user is the author of the comment
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:AUTHOR_OF]->(c:Comment {id: $comment_id})
            RETURN c;
            """,
            user_id=user_id, comment_id=int(comment_id)
        )

        comment = result.single()
        if not comment:
            return jsonify({'message': 'Unauthorized or Comment not found'}), 401

        # Delete the comment
        session.run(
            """
            MATCH (c:Comment {id: $comment_id})
            DETACH DELETE c;
            """,
            comment_id=int(comment_id)
        )
        
        return jsonify({'message': 'Comment deleted successfully'}), 200


def get_all_comments(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:Comment)
            RETURN c;
            """
        )
        
        comments = [dict(record['c']) for record in result]
        
        # Convert DateTime objects to strings
        for comment in comments:
            if 'created_at' in comment:
                comment['created_at'] = str(comment['created_at'])
                
            if 'last_edited_at' in comment:
                comment['last_edited_at'] = str(comment['last_edited_at'])
        
        
        return jsonify(comments), 200


def get_comments_by_post(request, post_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    try:
        post_id = int(post_id)  # Ensure the post_id is an integer
    except ValueError:
        return jsonify({'message': 'Invalid post ID'}), 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Post {id: $post_id})-[:HAS_COMMENT]->(c:Comment)
            RETURN c;
            """,
            post_id=post_id
        )
        
        comments = [dict(record['c']) for record in result]
        
        for comment in comments:
            if 'created_at' in comment:
                comment['created_at'] = str(comment['created_at'])
                
            if 'last_edited_at' in comment:
                comment['last_edited_at'] = str(comment['last_edited_at'])
                
                
        if not comments:
            return jsonify({'message': 'No comments found for this post'}), 404
        
        return jsonify(comments), 200

def like_comment(request, comment_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])

    with driver.session() as session:
        # Check if the comment exists
        result = session.run(
            """
            MATCH (c:Comment {id: $comment_id})
            RETURN c;
            """,
            comment_id=int(comment_id)
        )

        comment = result.single()
        if not comment:
            return jsonify({'message': 'Comment not found'}), 404

        # Create a LIKE relationship from the user to the comment
        session.run(
            """
            MATCH (u:User {id: $user_id}), (c:Comment {id: $comment_id})
            CREATE (u)-[:LIKED]->(c)
            """,
            user_id=user_id, comment_id=int(comment_id)
        )

        return jsonify({'message': 'Comment liked successfully'}), 200
