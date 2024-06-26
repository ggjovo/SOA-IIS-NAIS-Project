from neo4j import GraphDatabase
from flask import jsonify, current_app
import psycopg2
from auth import authenticate_user
from db_specs import db_config

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

def create_user(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    data = request.get_json()
    user_id = int(data.get('id'))
    username = data.get('username')
    role = data.get('role')

    with driver.session() as session:
        session.run(
            """
            CREATE (u:User {
                id: $user_id, username: $username, role: $role
            })
            """,
            user_id=user_id, username=username, role=role
        )
        
        return jsonify({'message': 'User created successfully'}), 201

def read_user(request, user_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    try:
        user_id = int(user_id)  # Ensure the user_id is an integer
    except ValueError:
        return jsonify({'message': 'Invalid user ID'}), 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u;
            """,
            user_id=user_id
        )
        
        users = [dict(record['u']) for record in result]
        if not users:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify(users), 200

def update_user(request, user_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    data = request.get_json()
    username = data.get('username')
    role = data.get('role')

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u;
            """,
            user_id=int(user_id)
        )

        existing_user = result.single()
        if not existing_user:
            return jsonify({'message': 'User not found'}), 404

        user_properties = existing_user['u']
        username = username if username is not None else user_properties['username']
        role = role if role is not None else user_properties['role']

        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            SET u.username = $username, u.role = $role
            RETURN u;
            """,
            user_id=int(user_id), username=username, role=role
        )

        updated_user = result.single()
        if not updated_user:
            return jsonify({'message': 'Failed to update user'}), 500

        return jsonify(dict(updated_user['u'])), 200

def delete_user(request, user_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u;
            """,
            user_id=int(user_id)
        )

        user = result.single()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        session.run(
            """
            MATCH (u:User {id: $user_id})
            DETACH DELETE u;
            """,
            user_id=int(user_id)
        )
        
        return jsonify({'message': 'User deleted successfully'}), 200

def get_all_users(request):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)
            RETURN u;
            """
        )
        
        users = [dict(record['u']) for record in result]
        return jsonify(users), 200

def rate_blog(request, blog_id):
    user_info, error_response, status_code = authenticate_request(request)
    if error_response:
        return error_response, status_code

    user_id = int(user_info['id'])
    data = request.get_json()
    rating = data.get('rating')

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id}), (b:Blog {id: $blog_id})
            MERGE (u)-[r:RATED]->(b)
            SET r.rating = $rating
            RETURN r;
            """,
            user_id=user_id, blog_id=int(blog_id), rating=rating
        )

        rating = result.single()
        if not rating:
            return jsonify({'message': 'Failed to rate blog'}), 500

        return jsonify(dict(rating['r'])), 200
