from flask import jsonify, current_app
import psycopg2
from db_specs import db_config
import requests
from datetime import datetime
import random

def saga_orchestration_create_blog(user_id, title, description, token):
    blog_id = None

    try:
        # Step 1: Create Blog Entry in the Database
        blog_id = create_blog_entry(user_id, title, description)
        
        # Step 2: Notify Neo4j Service
        notify_recommender_service(blog_id, title, description, token)
        
        return jsonify({'message': 'Blog created successfully'}), 201

    except Exception as e:
        # Rollback if there is any failure
        if blog_id:
            rollback_blog_creation(blog_id)
        return jsonify({'message': 'Error creating blog. Rolled back.', 'error': str(e)}), 500


def create_blog_entry(user_id, title, description):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO blogs (user_id, title, description) VALUES (%s, %s, %s) RETURNING id", 
                       (user_id, title, description))
        blog_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return blog_id
    except Exception as e:
        raise Exception(f"Error creating blog entry: {str(e)}")


def notify_recommender_service(blog_id, title, description, token):
    # Introducing a 90% probability of error
    if random.random() < 0.9:
        raise Exception("Simulated error for testing rollback")

    recommender_url = "http://blog_recommender:8085/blogs"
    recommender_data = {
        'blog_id': blog_id,
        'title': title,
        'description': description,
        'created_at': datetime.now().isoformat(),  # Or any suitable timestamp format
        "token": token
    }
    
    recommender_response = requests.post(recommender_url, json=recommender_data)
    if recommender_response.status_code != 201:
        raise Exception(f"Recommender service error: {recommender_response.status_code, recommender_data}")


def rollback_blog_creation(blog_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blogs WHERE id = %s", (blog_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise Exception(f"Error rolling back blog creation: {str(e)}")
