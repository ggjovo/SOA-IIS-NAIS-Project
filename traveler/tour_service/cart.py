from flask import jsonify, current_app
import psycopg2
from psycopg2.extras import execute_values
from auth import authenticate_user
from db_specs import db_config
from datetime import datetime

def add_to_cart(request, tour_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])
    quantity = request.json.get('quantity')

    # Check if the tour exists
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM shoppingcart WHERE tour_id = %s AND user_id = %s",
                       (tour_id, user_id))
        existing_quantity = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'message': 'Error checking if tour with id %s exists' % tour_id, 'error': str(e)}), 500

    # If the tour is already in the cart, update the quantity
    if existing_quantity:
        new_quantity = existing_quantity[0] + quantity  # Increment quantity
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Update quantity in shopping cart
            cursor.execute("UPDATE shoppingcart SET quantity = %s WHERE tour_id = %s AND user_id = %s", 
                           (new_quantity, tour_id, user_id))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'message': 'Shopping cart updated successfully'}), 200
        except Exception as e:
            return jsonify({'message': 'Error updating shopping cart', 'error': str(e)}), 500
    else:
        # If the tour is not in the cart, insert a new record
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Insert the new tour into shopping cart
            cursor.execute("INSERT INTO shoppingcart (tour_id, quantity, user_id) VALUES (%s, %s, %s)", 
                           (tour_id, quantity, user_id))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'message': 'Tour added to shopping cart successfully'}), 201
        except Exception as e:
            return jsonify({'message': 'Error adding tour to shopping cart', 'error': str(e)}), 500

def remove_all_from_cart(request, tour_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Delete all entries from the shopping cart for the user
        cursor.execute("DELETE FROM shoppingcart WHERE user_id = %s and tour_id = %s", (user_id, tour_id))

        # Commit changes and close cursor and connection
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'All tours with the id %s removed from shopping cart successfully' %tour_id}), 200
    except Exception as e:
        return jsonify({'message': 'Error removing all tours from shopping cart', 'error': str(e)}), 500

def remove_from_cart(request, tour_id):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    # Check if the tour exists in the cart
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM shoppingcart WHERE tour_id = %s AND user_id = %s",
                       (tour_id, user_id))
        existing_quantity = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'message': 'Error checking if tour with id %s exists' % tour_id, 'error': str(e)}), 500

    # If the tour is in the cart, update the quantity
    if existing_quantity:
        current_quantity = existing_quantity[0]
        if current_quantity > 1:
            new_quantity = current_quantity - 1  # Decrement quantity
            try:
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor()

                # Update quantity in shopping cart
                cursor.execute("UPDATE shoppingcart SET quantity = %s WHERE tour_id = %s AND user_id = %s", 
                               (new_quantity, tour_id, user_id))

                conn.commit()
                cursor.close()
                conn.close()

                return jsonify({'message': 'Shopping cart updated successfully'}), 200
            except Exception as e:
                return jsonify({'message': 'Error updating shopping cart', 'error': str(e)}), 500
        else:
            # If the quantity is 1, remove the tour from the cart
            try:
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor()

                # Delete from shopping cart
                cursor.execute("DELETE FROM shoppingcart WHERE tour_id = %s AND user_id = %s", 
                               (tour_id, user_id))

                conn.commit()
                cursor.close()
                conn.close()

                return jsonify({'message': 'Tour removed from shopping cart successfully'}), 200
            except Exception as e:
                return jsonify({'message': 'Error while removing tour shopping cart', 'error': str(e)}), 500

def check_out(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        # Fetch all tours along with their tags that are in the user's shopping cart
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
                first_checkpoint.checkpoint_positions AS first_checkpoint_position,
                shoppingcart.quantity
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
            JOIN shoppingcart ON tours.id = shoppingcart.tour_id
            WHERE shoppingcart.user_id = %s
            GROUP BY tours.id, tours.title, tours.description, tours.duration, tours.price, tours.difficulty, tours.status, first_checkpoint.checkpoint_names, first_checkpoint.checkpoint_latitude, first_checkpoint.checkpoint_longitude, first_checkpoint.checkpoint_positions, shoppingcart.quantity;
        """, (user_id,))

        tours_with_tags = []
        row = cursor.fetchone()

        # Check if row is None
        if row is None:
            return jsonify({'message': 'No data found'}), 404

        # Extract column names from cursor description
        columns = [desc[0] for desc in cursor.description]        
        total_price = 0.0

        for row in cursor.fetchall():
            tour = {columns[i]: value for i, value in enumerate(row)}
            tour['tags'] = tour['tags'] if tour['tags'] is not None else []
            
            # Extract price and quantity
            price_str = tour['price']
            quantity = tour['quantity']
            currency = price_str.split(' ')[1]  # Extract currency from price
            price = float(price_str.split(' ')[0])  # Convert price to float, assuming format "amount currency"
            
            # Convert price to RSD if currency is not RSD
            if currency.lower() != 'din':
                price = convert_to_rsd(currency.lower(), price)
            
            # Calculate total price
            total_price += price * quantity
            
            tours_with_tags.append(tour)

        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({'message': 'Error during return on total_price', 'error': str(e)}), 500

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        checkout_date = datetime.now()

        # Insert checkout record
        cursor.execute("INSERT INTO checkout (user_id, total_price, checkout_date) VALUES (%s, %s, %s) RETURNING id", (user_id, total_price, checkout_date))
        checkout_id = cursor.fetchone()[0]

        # Fetch all tours from shopping cart
        cursor.execute("SELECT tour_id, quantity FROM shoppingcart WHERE user_id = %s", (user_id,))
        cart_items = cursor.fetchall()

        # Upsert into ownedTours table
        upsert_query = """
            INSERT INTO ownedTours (user_id, tour_id, quantity) 
            VALUES %s 
            ON CONFLICT (user_id, tour_id) 
            DO UPDATE SET quantity = ownedTours.quantity + EXCLUDED.quantity
        """
        execute_values(cursor, upsert_query, [(user_id, tour_id, quantity) for tour_id, quantity in cart_items])


        # Delete records from shopping cart
        cursor.execute("DELETE FROM shoppingcart WHERE user_id = %s", (user_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Checkout successful', 'checkout_id': checkout_id, 'total_price': total_price, 'checkout_date': checkout_date}), 200
    except Exception as e:
        return jsonify({'message': 'Error during checkout', 'error': str(e)}), 500

def view_cart(request):
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Unauthorized'}), 401

    # Authenticate the user
    authenticated, user_info = authenticate_user(token)
    if not authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    if user_info['role'] != 'tourist':
        return jsonify({'message': 'Unauthorized'}), 401

    user_id = int(user_info['id'])

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        # Fetch all tours along with their tags that are in the user's shopping cart
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
                first_checkpoint.checkpoint_positions AS first_checkpoint_position,
                shoppingcart.quantity
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
            JOIN shoppingcart ON tours.id = shoppingcart.tour_id
            WHERE shoppingcart.user_id = %s
            GROUP BY tours.id, tours.title, tours.description, tours.duration, tours.price, tours.difficulty, tours.status, first_checkpoint.checkpoint_names, first_checkpoint.checkpoint_latitude, first_checkpoint.checkpoint_longitude, first_checkpoint.checkpoint_positions, shoppingcart.quantity;
        """, (user_id,))

        tours_with_tags = []
        columns = [desc[0] for desc in cursor.description]  # Get column names from cursor
        
        total_price = 0.0

        for row in cursor.fetchall():
            tour = {columns[i]: value for i, value in enumerate(row)}
            tour['tags'] = tour['tags'] if tour['tags'] is not None else []
            
            # Extract price and quantity
            price_str = tour['price']
            quantity = tour['quantity']
            currency = price_str.split(' ')[1]  # Extract currency from price
            price = float(price_str.split(' ')[0])  # Convert price to float, assuming format "amount currency"
            
            # Convert price to RSD if currency is not RSD
            if currency.lower() != 'din':
                price = convert_to_rsd(currency.lower(), price)
            
            # Calculate total price
            total_price += price * quantity
            
            tours_with_tags.append(tour)

        cursor.close()
        conn.close()

        return jsonify({'tours': tours_with_tags, 'total_price': total_price}), 200
    except Exception as e:
        return jsonify({'message': 'Error retrieving cart', 'error': str(e)}), 500

# Currency conversion function
def convert_to_rsd(currency, price):
    exchange_rates = {
        'usd': 107.72,
        'eur': 117.13
    }

    currency = currency.lower()
    if currency not in exchange_rates:
        raise ValueError('Invalid currency')

    exchange_rate = exchange_rates[currency]
    converted_price = price * exchange_rate
    return converted_price

