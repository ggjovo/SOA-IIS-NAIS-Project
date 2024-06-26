from flask import jsonify, current_app
import psycopg2
from auth import authenticate_user
from db_specs import db_config

from pymongo import MongoClient

uri = "mongodb://traveler-mongodb-1"
client = MongoClient(uri)
db = client['tourist']

# Define collections
tours_collection = db['tours']
tags_collection = db['tags']
checkpoint_collection = db['checkpoints']

def get_all_tours_guide(request):
    try:
        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Unauthorized'}), 401

        # Authenticate the user
        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if user_info['role'] != 'guide':
            return jsonify({'message': 'Unauthorized'}), 401
        
        user_id = user_info['id']

        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Fetch all tours along with their tags and checkpoint data
        cursor.execute("""
            SELECT 
                tours.id,
                tours.title, 
                tours.description, 
                tours.duration, 
                tours.price, 
                tours.difficulty, 
                tours.status, 
                tags.tags,
                checkpoints.checkpoint_names,
                checkpoints.checkpoint_longitude,
                checkpoints.checkpoint_latitude,
                checkpoints.checkpoint_positions
            FROM tours
            LEFT JOIN (
                SELECT tour_id, array_agg(name) AS tags
                FROM tags
                GROUP BY tour_id
            ) AS tags ON tours.id = tags.tour_id
            LEFT JOIN (
                SELECT tour_id,
                    array_agg(name) AS checkpoint_names,
                    array_agg(longitude) AS checkpoint_longitude,
                    array_agg(latitude) AS checkpoint_latitude,
                    array_agg(position) AS checkpoint_positions
                FROM checkpoints
                GROUP BY tour_id
            ) AS checkpoints ON tours.id = checkpoints.tour_id
            WHERE tours.guide_id = %s;
        """, (user_id,))
        
        tours_with_tags = []
        columns = [desc[0] for desc in cursor.description]  # Get column names from cursor
        
        for row in cursor.fetchall():
            tour = {columns[i]: value for i, value in enumerate(row)}
            tour['tags'] = tour['tags'] if tour['tags'] is not None else []
            tours_with_tags.append(tour)
        
        cursor.close()
        conn.close()
        
        return jsonify({'tours': tours_with_tags}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({'message': 'Error retrieving tours', 'error': str(e)}), 500



# Function to handle getting all tours along with their tags
def get_all_tours_tourist(request):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Unauthorized'}), 401

        # Authenticate the user
        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if user_info['role'] != 'tourist':
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Fetch all tours along with their tags
        cursor.execute("""
            SELECT 
                tours.id,
                tours.title, 
                tours.description, 
                tours.duration, 
                tours.price, 
                tours.difficulty, 
                tours.status, 
                array_agg(tags.name) AS tags,
                first_checkpoint.checkpoint_names AS first_checkpoint_name,
                first_checkpoint.checkpoint_latitude AS first_checkpoint_latitude,
                first_checkpoint.checkpoint_longitude AS first_checkpoint_longitude,
                first_checkpoint.checkpoint_positions AS first_checkpoint_position
            FROM tours
            LEFT JOIN (
                SELECT tour_id,
                    array_agg(name) AS checkpoint_names,
                    array_agg(longitude) AS checkpoint_longitude,
                    array_agg(latitude) AS checkpoint_latitude,
                    array_agg(position) AS checkpoint_positions
                FROM (
                    SELECT tour_id, name, longitude, latitude, position
                    FROM checkpoints
                    WHERE (tour_id, position) IN (
                        SELECT tour_id, MIN(position)
                        FROM checkpoints
                        GROUP BY tour_id
                    )
                ) AS min_position_checkpoints
                GROUP BY tour_id
            ) AS first_checkpoint ON tours.id = first_checkpoint.tour_id
            LEFT JOIN tags ON tours.id = tags.tour_id
            GROUP BY tours.id, tours.title, tours.description, tours.duration, tours.price, tours.difficulty, tours.status, first_checkpoint.checkpoint_names, first_checkpoint.checkpoint_latitude, first_checkpoint.checkpoint_longitude, first_checkpoint.checkpoint_positions;

        """)
        
        tours_with_tags = []
        columns = [desc[0] for desc in cursor.description]  # Get column names from cursor
        
        for row in cursor.fetchall():
            tour = {columns[i]: value for i, value in enumerate(row)}
            tour['tags'] = tour['tags'] if tour['tags'] is not None else []
            tours_with_tags.append(tour)
                
        cursor.close()
        conn.close()
        
        return jsonify({'tours': tours_with_tags}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({'message': 'Error retrieving tours', 'error': str(e)}), 500


def get_tag_ids_by_tour_id(tour_id):
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Execute the query to fetch tag IDs
        cursor.execute("SELECT id FROM tags WHERE tour_id = %s", (tour_id,))
        
        # Fetch all tag IDs
        tag_ids = [row[0] for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return tag_ids
    except Exception as e:
        print("Error:", e)
        return None

def insert_tags_for_tour(tour_id, tags):
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Insert each tag for the given tour ID
        for tag in tags:
            cursor.execute("INSERT INTO tags (name, tour_id) VALUES (%s, %s)",
                           (tag, tour_id))
        
        # Commit the changes and close the cursor and connection
        conn.commit()
        cursor.close()
        conn.close()
        
        tag_ids = get_tag_ids_by_tour_id(tour_id)

        for tag_id in tag_ids:
            tags_collection.insert_one({'_id': tag_id ,'tour_id': tour_id, 'name': tag})
        
        return jsonify({'message': 'Tags inserted successfully'}), 200
    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        
        # Return an error message
        return jsonify({'message': 'Error inserting tags', 'error': str(e)}), 500


# Function to handle creating new tours
def create_tour(request):    

    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401
    
    if user_info['role'] != 'guide':
        return jsonify({'message': 'Unauthorized'}), 401

    # Extract data from request
    title = request.json.get('title')
    description = request.json.get('description')
    duration = request.json.get('duration')
    difficulty = request.json.get('difficulty')
    tags = request.json.get('tags')
    price = request.json.get('price')
    status = request.json.get('status', 'draft')  # default to 'draft' if not provided

    if not all([title, description, duration, difficulty, price]):
        return jsonify({'message': 'Incomplete data provided'}), 400

    user_id = int(user_info['id'])


    # Connect to PostgreSQL and insert the new tour post
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tours (title, description, duration, difficulty, price, status, guide_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                       (title, description, duration, difficulty, price, status, user_id))
        
        # Fetch the newly inserted tour ID
        tour_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        tour_data = {
            '_id': tour_id,
            'title': title,
            'description': description,
            'duration': duration,
            'difficulty': difficulty,
            'price': price,
            'status': status
        }

        # Insert tour data into MongoDB
        tours_collection.insert_one(tour_data)

        # Insert tags for the newly created tour
        insert_tags_for_tour(tour_id, tags)

        return jsonify({'message': 'Tour created successfully', 'tour_id': tour_id}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating tour', 'error': str(e)}), 500

def get_checkpoints_for_tour(tour_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tour_id, latitude, longitude, name, position FROM checkpoints WHERE tour_id = %s", (tour_id,))
        checkpoints = []
        for row in cursor.fetchall():
            checkpoint_id, tour_id, latitude, longitude, name, position = row
            checkpoint_data = {
                '_id': checkpoint_id,
                'tour_id': tour_id,
                'latitude': float(latitude),
                'longitude': float(longitude),
                'name': name,
                'position': int(position)
            }
            checkpoints.append(checkpoint_data)
        
        cursor.close()
        conn.close()
        
        return checkpoints
    except Exception as e:
        print("Error fetching checkpoints:", e)
        return None

# Function to handle adding checkpoints
def add_checkpoint(request, tour_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'guide':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    checkpoints = request.json

    # Check if the tour is made by that user
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tours WHERE guide_id = %s",
                       (user_id,))
        creator = cursor.fetchone()[0] > 0
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'message': 'Error checking if user created the specific tour with id %s' % tour_id, 'error': str(e)}), 500

    if not creator:
        return jsonify({'message': 'You need to be the creator of this tour before adding checkpoints'}), 403

    # Connect to PostgreSQL and insert the new checkpoint
    try:
        for checkpoint in checkpoints:
            latitude = checkpoint.get('latitude')
            longitude = checkpoint.get('longitude')
            name = checkpoint.get('name')
            position = checkpoint.get('position')

            if not all([latitude, longitude, name, position]):
                return jsonify({'message': 'Incomplete data provided for a checkpoint'}), 400

            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Insert the new checkpoint into PostgreSQL
            cursor.execute("INSERT INTO checkpoints (tour_id, latitude, longitude, name, position) VALUES (%s, %s, %s, %s, %s)", 
                       (tour_id, latitude, longitude, name, position))

            conn.commit()
            cursor.close()
            conn.close()

        checkpointsMongo = get_checkpoints_for_tour(tour_id)
        checkpoint_collection.insert_many(checkpointsMongo)

        return jsonify({'message': 'Checkpoint added successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error adding checkpoint', 'error': str(e)}), 500

# Function to handle deleting tours
def delete_tour(tour_id):
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Delete the tour
        cursor.execute("DELETE FROM tours WHERE id = %s", (tour_id,))
        conn.commit()

        cursor.close()
        conn.close()

        # Delete from MongoDB
        tours_collection.delete_one({'_id': tour_id})

        return jsonify({'message': 'Tour deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': 'Error deleting tour', 'error': str(e)}), 500

def get_owned_tours(request):
    try:
        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Unauthorized'}), 401

        # Authenticate the user
        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if user_info['role'] != 'tourist':
            return jsonify({'message': 'Unauthorized'}), 401
        
        user_id = user_info['id']

        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Fetch owned tours along with their data and quantity
        cursor.execute("""
            SELECT 
                tours.id,
                tours.title, 
                tours.description, 
                tours.duration, 
                tours.price, 
                tours.difficulty, 
                tours.status, 
                tags.tags,
                checkpoints.checkpoint_names,
                checkpoints.checkpoint_longitude,
                checkpoints.checkpoint_latitude,
                checkpoints.checkpoint_positions,
                ownedTours.quantity,
                ownedTours.id as ownedTours_id
            FROM tours
            LEFT JOIN (
                SELECT tour_id, array_agg(name) AS tags
                FROM tags
                GROUP BY tour_id
            ) AS tags ON tours.id = tags.tour_id
            LEFT JOIN (
                SELECT tour_id,
                    array_agg(name) AS checkpoint_names,
                    array_agg(longitude) AS checkpoint_longitude,
                    array_agg(latitude) AS checkpoint_latitude,
                    array_agg(position) AS checkpoint_positions
                FROM checkpoints
                GROUP BY tour_id
            ) AS checkpoints ON tours.id = checkpoints.tour_id
            INNER JOIN ownedTours ON tours.id = ownedTours.tour_id
            WHERE ownedTours.user_id = %s;
        """, (user_id,))
        
        owned_tours_with_data = []
        columns = [desc[0] for desc in cursor.description]  # Get column names from cursor
        
        for row in cursor.fetchall():
            tour = {columns[i]: value for i, value in enumerate(row)}
            tour['tags'] = tour['tags'] if tour['tags'] is not None else []
            owned_tours_with_data.append(tour)
        
        cursor.close()
        conn.close()
        
        return jsonify({'owned_tours': owned_tours_with_data}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({'message': 'Error retrieving owned tours', 'error': str(e)}), 500
    
def add_review(request, tour_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = user_info['id']
    review_text = request.json.get('review_text')
    rating = request.json.get('rating')

    if not review_text or not rating:
        return jsonify({'message': 'Incomplete data provided'}), 400

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if the user has purchased the tour
        cursor.execute("SELECT COUNT(*) FROM ownedTours WHERE user_id = %s AND tour_id = %s", (user_id, tour_id))
        has_purchased = cursor.fetchone()[0] > 0
        
        if not has_purchased:
            return jsonify({'message': 'User has not purchased this tour'}), 403
        
        # Check if the user has visited at least half of the key checkpoints
        cursor.execute("SELECT COUNT(*) FROM checkpoints WHERE tour_id = %s", (tour_id,))
        total_checkpoints = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM tourExecutionCheckpoints tec
            JOIN tourExecution te ON tec.tour_execution_id = te.id
            WHERE te.user_id = %s AND te.tour_id = %s
        """, (user_id, tour_id))
        visited_checkpoints = cursor.fetchone()[0]

        if visited_checkpoints < total_checkpoints / 2:
            return jsonify({'message': 'User has not visited enough checkpoints to leave a review'}), 403

        # Insert the review
        cursor.execute("INSERT INTO reviews (tour_id, user_id, review_text, rating) VALUES (%s, %s, %s, %s)",
                       (tour_id, user_id, review_text, rating))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Review added successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error adding review', 'error': str(e)}), 500


def check_review(request, tour_id):
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
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE user_id = %s AND tour_id = %s", (user_id, tour_id))
        review_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({'review_count': review_count}), 200
    except Exception as e:
        return jsonify({'message': 'Error checking review', 'error': str(e)}), 500
    
def get_average_rating(tour_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT AVG(rating) FROM reviews WHERE tour_id = %s", (tour_id,))
        average_rating = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return average_rating
    except Exception as e:
        print("Error calculating average rating:", e)
        return None
    
def update_review(request, tour_id):
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
        # Provera da li korisnik ima već napisanu recenziju
        cursor.execute("SELECT id FROM reviews WHERE user_id = %s AND tour_id = %s", (user_id, tour_id))
        review_id = cursor.fetchone()

        if review_id:
            review_text = request.json.get('review_text')
            rating = request.json.get('rating')
            # Ažuriranje recenzije
            cursor.execute("UPDATE reviews SET review_text = %s, rating = %s WHERE id = %s", (review_text, rating, review_id))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Review updated successfully'}), 200
        else:
            return jsonify({'message': 'Review not found for the user'}), 404
    except Exception as e:
        return jsonify({'message': 'Error updating review', 'error': str(e)}), 500

def get_all_tours_tourist(request):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Unauthorized'}), 401

        # Authenticate the user
        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if user_info['role'] != 'tourist':
            return jsonify({'message': 'Unauthorized'}), 401
        
        cursor.execute("""
            SELECT 
                tours.id,
                tours.title, 
                tours.description, 
                tours.duration, 
                tours.price, 
                tours.difficulty, 
                tours.status, 
                array_agg(tags.name) AS tags,
                first_checkpoint.checkpoint_names AS first_checkpoint_name,
                first_checkpoint.checkpoint_latitude AS first_checkpoint_latitude,
                first_checkpoint.checkpoint_longitude AS first_checkpoint_longitude,
                first_checkpoint.checkpoint_positions AS first_checkpoint_position
            FROM tours
            LEFT JOIN (
                SELECT tour_id,
                    array_agg(name) AS checkpoint_names,
                    array_agg(longitude) AS checkpoint_longitude,
                    array_agg(latitude) AS checkpoint_latitude,
                    array_agg(position) AS checkpoint_positions
                FROM (
                    SELECT tour_id, name, longitude, latitude, position
                    FROM checkpoints
                    WHERE (tour_id, position) IN (
                        SELECT tour_id, MIN(position)
                        FROM checkpoints
                        GROUP BY tour_id
                    )
                ) AS min_position_checkpoints
                GROUP BY tour_id
            ) AS first_checkpoint ON tours.id = first_checkpoint.tour_id
            LEFT JOIN tags ON tours.id = tags.tour_id
            GROUP BY tours.id, tours.title, tours.description, tours.duration, tours.price, tours.difficulty, tours.status, first_checkpoint.checkpoint_names, first_checkpoint.checkpoint_latitude, first_checkpoint.checkpoint_longitude, first_checkpoint.checkpoint_positions;
        """)
        
        tours_with_tags = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in cursor.fetchall():
            tour = {columns[i]: value for i, value in enumerate(row)}
            tour['tags'] = tour['tags'] if tour['tags'] is not None else []
            tour_id = tour['id']
            tour['average_rating'] = get_average_rating(tour_id)
            
            cursor.execute("SELECT review_text, rating FROM reviews WHERE tour_id = %s", (tour_id,))
            tour['reviews'] = [{'review_text': review[0], 'rating': review[1]} for review in cursor.fetchall()]
            
            tours_with_tags.append(tour)
                
        cursor.close()
        conn.close()
        
        return jsonify({'tours': tours_with_tags}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving tours', 'error': str(e)}), 500

def get_tour_details(request, tour_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        token = request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Unauthorized'}), 401

        # Authenticate the user
        authenticated, user_info = authenticate_user(token)
        if not authenticated:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if user_info['role'] != 'tourist':
            return jsonify({'message': 'Unauthorized'}), 401
        
        cursor.execute("""
            SELECT 
                tours.id,
                tours.title, 
                tours.description, 
                tours.duration, 
                tours.price, 
                tours.difficulty, 
                tours.status, 
                array_agg(tags.name) AS tags,
                first_checkpoint.checkpoint_names AS first_checkpoint_name,
                first_checkpoint.checkpoint_latitude AS first_checkpoint_latitude,
                first_checkpoint.checkpoint_longitude AS first_checkpoint_longitude,
                first_checkpoint.checkpoint_positions AS first_checkpoint_position
            FROM tours
            LEFT JOIN (
                SELECT tour_id,
                    array_agg(name) AS checkpoint_names,
                    array_agg(longitude) AS checkpoint_longitude,
                    array_agg(latitude) AS checkpoint_latitude,
                    array_agg(position) AS checkpoint_positions
                FROM (
                    SELECT tour_id, name, longitude, latitude, position
                    FROM checkpoints
                    WHERE (tour_id, position) IN (
                        SELECT tour_id, MIN(position)
                        FROM checkpoints
                        GROUP BY tour_id
                    )
                ) AS min_position_checkpoints
                GROUP BY tour_id
            ) AS first_checkpoint ON tours.id = first_checkpoint.tour_id
            LEFT JOIN tags ON tours.id = tags.tour_id
            WHERE tours.id = %s
            GROUP BY tours.id, tours.title, tours.description, tours.duration, tours.price, tours.difficulty, tours.status, first_checkpoint.checkpoint_names, first_checkpoint.checkpoint_latitude, first_checkpoint.checkpoint_longitude, first_checkpoint.checkpoint_positions;
        """, (tour_id,))
        
        tour_data = cursor.fetchone()
        if not tour_data:
            return jsonify({'message': 'Tour not found'}), 404
        
        tour = {
            'id': tour_data[0],
            'title': tour_data[1],
            'description': tour_data[2],
            'duration': tour_data[3],
            'price': tour_data[4],
            'difficulty': tour_data[5],
            'status': tour_data[6],
            'tags': tour_data[7] if tour_data[7] else [],
            'first_checkpoint_name': tour_data[8],
            'first_checkpoint_latitude': tour_data[9],
            'first_checkpoint_longitude': tour_data[10],
            'first_checkpoint_position': tour_data[11]
        }
        
        tour['average_rating'] = get_average_rating(tour_id)
        
        cursor.execute("SELECT review_text, rating FROM reviews WHERE tour_id = %s", (tour_id,))
        tour['reviews'] = [{'review_text': review[0], 'rating': review[1]} for review in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'tour': tour}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving tour details', 'error': str(e)}), 500

# TODO: Function to handle editing tours

# TODO: Function to handle deleting checkpoints
'''
def edit_tour(request, comment_id):
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
        # Update comment only if the user_id matches and the comment_id exists
        cursor.execute("UPDATE comments SET comment_text = %s, last_edited_at = CURRENT_TIMESTAMP WHERE id = %s AND user_id = %s", 
                       (new_comment_text, comment_id, user_id))
        if cursor.rowcount == 0:  # Check if any rows were updated
            return jsonify({'message': 'Unauthorized: You are not the owner of this comment or the comment does not exist'}), 401
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Comment edited successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error editing comment', 'error': str(e)}), 500
'''
