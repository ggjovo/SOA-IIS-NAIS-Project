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

def create_blog(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])
    username = user_info['username']
    role = user_info['role']
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    created_at = data.get('created_at')
    blog_id = int(data.get('blog_id'))  # Make sure the key is 'blog_id'

    with driver.session() as session:
        # Check if user exists, if not create the user
        session.run(
            """
            MERGE (u:User {id: $user_id})
            ON CREATE SET u.username = $username, u.role = $role
            """,
            user_id=int(user_id), username=username, role=role
        )
        
        # Create the blog authored by the user
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            CREATE (u)-[:AUTHOR_OF]->(b:Blog {
                id: $blog_id, title: $title, description: $description, created_at: $created_at
            })
            RETURN b;
            """,
            user_id=int(user_id), blog_id=int(blog_id), title=title, description=description, created_at=created_at
        )

        blogs = [dict(record['b']) for record in result]
        current_app.logger.info("Results: %s", blogs)

        if not blogs:
            current_app.logger.error("No blogs created in Neo4j.")

        return jsonify(blogs), 201


def read_blog(request, blog_id):
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
            MATCH (b:Blog {id: $blog_id})
            RETURN b;
            """,
            blog_id=int(blog_id)
        )
        
        blogs = [dict(record['b']) for record in result]
        if not blogs:
            return jsonify({'message': 'Blog not found'}), 404
        
        for blog in blogs:
            if 'created_at' in blog:
                blog['created_at'] = str(blog['created_at'])
        
        return jsonify(blogs), 200


def update_blog(request, blog_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    created_at = data.get('created_at')

    with driver.session() as session:
        # Fetch the existing blog
        result = session.run(
            """
            MATCH (b:Blog {id: $blog_id})
            RETURN b;
            """,
            blog_id=int(blog_id)
        )

        existing_blog = result.single()
        if not existing_blog:
            return jsonify({'message': 'Blog not found'}), 404

        # Get the existing blog properties
        blog_properties = existing_blog['b']

        # Use existing values if not provided in the request
        title = title if title is not None else blog_properties['title']
        description = description if description is not None else blog_properties['description']
        created_at = created_at if created_at is not None else blog_properties['created_at']

        # Update the blog with the new values
        result = session.run(
            """
            MATCH (b:Blog {id: $blog_id})
            SET b.title = $title, b.description = $description, b.created_at = $created_at
            RETURN b;
            """,
            blog_id=int(blog_id), title=title, description=description, created_at=created_at
        )

        updated_blog = result.single()
        if not updated_blog:
            return jsonify({'message': 'Failed to update blog'}), 500

        return jsonify(dict(updated_blog['b'])), 200



def delete_blog(request, blog_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])

    with driver.session() as session:
        # Check if the user is the author of the blog
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:AUTHOR_OF]->(b:Blog {id: $blog_id})
            RETURN b;
            """,
            user_id=int(user_id), blog_id=int(blog_id)
        )

        blog = result.single()
        if not blog:
            return jsonify({'message': 'Unauthorized or Blog not found'}), 401

        # Delete the blog
        session.run(
            """
            MATCH (b:Blog {id: $blog_id})
            DETACH DELETE b;
            """,
            blog_id=int(blog_id)
        )
        
        return jsonify({'message': 'Blog deleted successfully'}), 200


def get_all_blogs(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    with driver.session() as session:
        result = session.run(
            """
            MATCH (b:Blog)
            RETURN b;
            """
        )
        
        blogs = [dict(record['b']) for record in result]
        
        # Convert DateTime objects to strings
        for blog in blogs:
            if 'created_at' in blog:
                blog['created_at'] = str(blog['created_at'])
        
        return jsonify(blogs), 200
