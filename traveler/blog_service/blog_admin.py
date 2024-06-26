from flask import jsonify
import psycopg2
from auth import authenticate_user
from db_specs import db_config

def get_average_rating_by_day(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    user_role = user_info.get('role')

    # Check if the user is an admin
    if user_role != 'admin':
        return jsonify({'message': 'Forbidden'}), 403

    # Connect to PostgreSQL and run the query to get average ratings by day
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE_TRUNC('day', created_at) AS day, AVG(rating) AS average_rating
            FROM platformreview
            GROUP BY day
            ORDER BY day ASC;
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format the results into the desired JSON structure
        average_ratings = {result[0].strftime("%Y-%m-%d"): result[1] for result in results}
        return jsonify(average_ratings), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving average ratings', 'error': str(e)}), 500
    
def get_platform_reviews(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    user_role = user_info.get('role')

    # Check if the user is an admin
    if user_role != 'admin':
        return jsonify({'message': 'Forbidden'}), 403

    # Connect to PostgreSQL and fetch all data related to platform reviews
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.user_id, u.Username, u.Role, u.Email, u.Blocked, pr.rating, pr.comment
            FROM PlatformReview pr
            INNER JOIN users u ON pr.user_id = u.ID;
        """)
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format the results into a list of dictionaries
        platform_reviews = []
        for review in reviews:
            platform_reviews.append({
                'user_id': review[0],
                'username': review[1],
                'user_role': review[2],
                'email': review[3],
                'blocked': review[4],
                'rating': review[5],
                'comment': review[6]
            })

        return jsonify({'platform_reviews': platform_reviews}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving platform reviews', 'error': str(e)}), 500
    
    
    
def block_user(request, user_id_to_block):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    user_role = user_info.get('role')

    # Check if the user is an admin
    if user_role != 'admin':
        return jsonify({'message': 'Forbidden'}), 403

    # Connect to PostgreSQL and toggle the user's blocked status
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if the user is already blocked
        cursor.execute("SELECT Blocked FROM users WHERE ID = %s", (user_id_to_block,))
        user_blocked = cursor.fetchone()[0]  # Fetch the blocked status
        new_blocked_status = not user_blocked  # Toggle the blocked status

        # Update the user's blocked status
        cursor.execute("UPDATE users SET Blocked = %s WHERE ID = %s", (new_blocked_status, user_id_to_block))
        conn.commit()
        cursor.close()
        conn.close()

        if new_blocked_status:
            return jsonify({'message': 'User blocked successfully'}), 200
        else:
            return jsonify({'message': 'User unblocked successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Error blocking/unblocking user', 'error': str(e)}), 500
        
        
        
        
