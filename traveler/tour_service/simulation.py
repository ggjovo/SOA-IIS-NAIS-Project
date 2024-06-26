from flask import jsonify, request
import psycopg2
from auth import authenticate_user
from db_specs import db_config
from datetime import datetime

def user_owns_tour(user_id, tour_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ownedTours WHERE user_id = %s AND tour_id = %s", (user_id, tour_id))
        result = cursor.fetchone()[0] > 0
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(e)
        return False

def start_tour(request, tour_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    authenticated, user_info = authenticate_user(token)
    if not authenticated or user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    if not user_owns_tour(user_id, tour_id):
        return jsonify({'message': 'You do not own this tour'}), 403

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tourExecution (user_id, tour_id, start_time) VALUES (%s, %s, %s) RETURNING id", (user_id, tour_id, datetime.now()))
        tour_execution_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tour started successfully', 'tour_execution_id': tour_execution_id}), 201
    except Exception as e:
        return jsonify({'message': 'Error starting tour', 'error': str(e)}), 500

def update_position(request, tour_execution_id):    
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    authenticated, user_info = authenticate_user(token)
    if not authenticated or user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    data = request.get_json()
    tour_id = data['tour_id']
    latitude = data['latitude']
    longitude = data['longitude']

    if not user_owns_tour(user_id, tour_id):
        return jsonify({'message': 'You do not own this tour'}), 403

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tourExecution
            SET latitude = %s, longitude = %s
            WHERE id = %s
            RETURNING id
        """, (latitude, longitude, tour_execution_id))
        if cursor.rowcount == 0:
            return jsonify({'message': 'Tour execution not found'}), 404

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Location updated', 'tour_execution_id': tour_execution_id, 'latitude': latitude, 'longitude': longitude}), 200
    except Exception as e:
        return jsonify({'message': 'Error updating location', 'error': str(e)}), 500


def end_tour(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    authenticated, user_info = authenticate_user(token)
    if not authenticated or user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Find the latest tour_execution_id for the current user
        cursor.execute("SELECT id FROM tourExecution WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        tour_execution_id = cursor.fetchone()[0]
        
        # Update end time for the tour execution
        cursor.execute("UPDATE tourExecution SET end_time = %s WHERE id = %s AND user_id = %s", (datetime.now(), tour_execution_id, user_id))
        conn.commit()

        # Fetch the total number of checkpoints for the given tour
        cursor.execute("""
            SELECT COUNT(*) FROM checkpoints WHERE tour_id = (
                SELECT tour_id FROM tourExecution WHERE id = %s
            )
        """, (tour_execution_id,))
        total_checkpoints = cursor.fetchone()[0]

        # Fetch the number of checkpoints already reached
        cursor.execute("""
            SELECT COUNT(*) FROM tourExecutionCheckpoints
            WHERE tour_execution_id = %s
        """, (tour_execution_id,))
        reached_checkpoints = cursor.fetchone()[0]

        # Calculate the remaining checkpoints to be marked as reached
        remaining_checkpoints = total_checkpoints - reached_checkpoints

        # Fetch the tour id from tourExecution
        cursor.execute("SELECT tour_id FROM tourExecution WHERE id = %s", (tour_execution_id,))
        tour_id = cursor.fetchone()[0]

        # Determine the starting checkpoint index
        starting_checkpoint_index = total_checkpoints - remaining_checkpoints + 1

        # Loop through remaining checkpoints and insert them into tourExecutionCheckpoints

        if starting_checkpoint_index <= total_checkpoints:
            for i in range(starting_checkpoint_index, total_checkpoints):
                cursor.execute("""
                    INSERT INTO tourExecutionCheckpoints (tour_execution_id, checkpoint_id, reached_at)
                    SELECT %s, id, %s FROM checkpoints WHERE tour_id = %s AND position = %s
                """, (tour_execution_id, datetime.now(), tour_id, i))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'Tour ended successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error ending tour', 'error': str(e)}), 500

def mark_checkpoint_as_reached(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    authenticated, user_info = authenticate_user(token)
    if not authenticated or user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    data = request.get_json()
    tour_execution_id = data['tour_execution_id']
    checkpoint_id = data['checkpoint_id']

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if the checkpoint has already been reached
        cursor.execute("""
            SELECT COUNT(*)
            FROM tourExecutionCheckpoints
            WHERE tour_execution_id = %s AND checkpoint_id = %s
        """, (tour_execution_id, checkpoint_id))
        if cursor.fetchone()[0] > 0:
            return jsonify({'message': 'Checkpoint already reached'}), 200

        # Mark the checkpoint as reached
        cursor.execute("""
            INSERT INTO tourExecutionCheckpoints (tour_execution_id, checkpoint_id, reached_at)
            VALUES (%s, %s, %s)
        """, (tour_execution_id, checkpoint_id, datetime.now()))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({'message': 'Checkpoint marked as reached'}), 200
    except Exception as e:
        return jsonify({'message': 'Error marking checkpoint as reached', 'error': str(e)}), 500

    
def delete_owned_tour(request, ownedtours_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    authenticated, user_info = authenticate_user(token)
    if not authenticated or user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ownedTours WHERE id = %s", (ownedtours_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Owned tour removed successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error deleting tour', 'error': str(e)}), 500