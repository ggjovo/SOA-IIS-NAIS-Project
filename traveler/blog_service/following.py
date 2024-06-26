from flask import Blueprint, request, jsonify
import psycopg2
from auth import authenticate_user
from db_specs import db_config
from neo4j import GraphDatabase

#following_routes = Blueprint('following', __name__)

# Neo4j connection
neo4j_uri = "bolt://neo4j:7687"
neo4j_user = "neo4j"  # Default user
neo4j_password = "123456789"

#following_routes = Blueprint('following', __name__)

def get_user_from_postgres(user_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'password': user[2],
                'email': user[3],
                'role': user[4],
                'blocked': user[5]
            }
    except Exception as e:
        print(f"Error fetching user from PostgreSQL: {e}")
    return None

def create_following_neo4j(follower_id, following_id):
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        with driver.session() as session:
            # Ensure follower exists in Neo4j
            result = session.run(
                "MERGE (f:User {id: $follower_id}) RETURN f",
                follower_id=int(follower_id)
            )
            if result.single() is None:
                user_data = get_user_from_postgres(follower_id)
                if user_data:
                    session.run(
                        """
                        MERGE (u:User {id: $id})
                        ON CREATE SET u.username = $username, u.role = $role
                        """,
                        id=user_data['id'], username=user_data['username'], role=user_data['role']
                    )

            # Ensure following exists in Neo4j
            result = session.run(
                "MERGE (f:User {id: $following_id}) RETURN f",
                following_id=int(following_id)
            )
            if result.single() is None:
                user_data = get_user_from_postgres(following_id)
                if user_data:
                    session.run(
                        """
                        MERGE (u:User {id: $id})
                        ON CREATE SET u.username = $username, u.role = $role
                        """,
                        id=user_data['id'], username=user_data['username'], role=user_data['role']
                    )

            # Create the FOLLOWS relationship
            session.run(
                """
                MATCH (follower:User {id: $follower_id}), (following:User {id: $following_id})
                MERGE (follower)-[:FOLLOWS]->(following)
                """,
                follower_id=int(follower_id), following_id=int(following_id)
            )


def follow_user(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    follower_id = user_info['id']
    following_id = request.json.get('following_id')

    if not all([follower_id, following_id]):
        return jsonify({'message': 'Incomplete data provided'}), 400

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_followings (follower_id, following_id) VALUES (%s, %s)",
            (follower_id, following_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        create_following_neo4j(follower_id, following_id)

        return jsonify({'message': 'User followed successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error following user', 'error': str(e)}), 500

# Route to handle unfollowing a user
#@following_routes.route('/unfollow', methods=['POST'])
def unfollow_user(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401
    
    follower_id = user_info["id"]
    following_id = request.json.get('following_id')

    if not all([follower_id, following_id]):
        return jsonify({'message': 'Incomplete data provided'}), 400

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_followings WHERE follower_id = %s AND following_id = %s", 
                       (follower_id, following_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Remove the relationship from Neo4j
        with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
            with driver.session() as session:
                session.run(
                    "MATCH (follower:User {id: $follower_id})-[r:FOLLOWS]->(following:User {id: $following_id}) "
                    "DELETE r",
                    follower_id=follower_id, following_id=following_id
                )
                
        return jsonify({'message': 'User unfollowed successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error unfollowing user', 'error': str(e)}), 500
