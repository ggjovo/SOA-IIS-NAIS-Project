from flask import Blueprint
from flask import request, jsonify
import requests
from auth import authenticate_user
from tour import add_checkpoint, create_tour, get_all_tours_guide, get_all_tours_tourist, delete_tour, get_owned_tours, add_review, get_average_rating, get_tour_details, check_review, update_review
from cart import add_to_cart, remove_from_cart, check_out, view_cart, remove_all_from_cart
from simulation import start_tour, update_position, end_tour, delete_owned_tour, mark_checkpoint_as_reached

tour_routes = Blueprint('tour', __name__)
cart_routes = Blueprint('cart', __name__)
simulation_routes = Blueprint('simulation', __name__)

# Route to handle showing all guide tours to guide
@tour_routes.route('/show_tours_guide', methods=['GET'])
def create_get_all_tours_guide():
    return get_all_tours_guide(request)

# Route to handle showing all tours to user with reduced info
@tour_routes.route('/show_tours_tourist', methods=['GET'])
def create_get_all_tours_tourist():
    return get_all_tours_tourist(request)

# Route to handle creating new tour
@tour_routes.route('/createtour', methods=['POST'])
def create_tour_route():
    return create_tour(request)

# Route to handle add checkpoints on tour
@tour_routes.route('/addcheckpoint/<int:tour_id>', methods=['PUT'])
def add_checkpoint_route(tour_id):
    return add_checkpoint(request, tour_id)

# Route to handle delete tour
@tour_routes.route('/delete_tour/<int:tour_id>', methods=['DELETE'])
def delete_tour_route(tour_id):
    return delete_tour(tour_id)

@tour_routes.route('/owned_tours', methods=['GET'])
def get_owned_tours_route():
    return get_owned_tours(request)

@tour_routes.route('/add_review/<int:tour_id>', methods=['POST'])
def add_review_route(tour_id):
    return add_review(request, tour_id)

@tour_routes.route('/check_review/<int:tour_id>', methods=['GET'])
def check_review_route(tour_id):
    return check_review(request, tour_id)

@tour_routes.route('/update_review/<int:tour_id>', methods=['PUT'])
def update_review_route(tour_id):
    return update_review(request, tour_id)

@tour_routes.route('/average_rating/<int:tour_id>', methods=['GET'])
def average_rating_route(tour_id):
    return get_average_rating(tour_id)

@tour_routes.route('/tour_details/<int:tour_id>', methods=['GET'])
def get_tour_details_route(tour_id):
    return get_tour_details(request, tour_id)


# Cart

# Route to handle add to cart
@cart_routes.route('/add_to_cart/<int:tour_id>', methods=['PUT'])
def add_to_cart_route(tour_id):
    return add_to_cart(request, tour_id)

# Route to handle remove from cart
@cart_routes.route('/remove_from_cart/<int:tour_id>', methods=['DELETE'])
def remove_from_cart_route(tour_id):
    return remove_from_cart(request, tour_id)

# Route to handle remove all from cart
@cart_routes.route('/remove_all_from_cart/<int:tour_id>', methods=['DELETE'])
def remove_all_from_cart_route(tour_id):
    return remove_all_from_cart(request, tour_id)

# Route to handle checkout
@cart_routes.route('/check_out', methods=['DELETE'])
def check_out_route():
    return check_out(request)

# Route view cart
@cart_routes.route('/view_cart', methods=['GET'])
def view_cart_route():
    return view_cart(request)


# Tour start (simulation)

# Route start tour
@simulation_routes.route('/start_tour/<int:tour_id>', methods=['POST'])
def start_tour_route(tour_id):
    return start_tour(request, tour_id)

@simulation_routes.route('/update_position/<int:tour_execution_id>', methods=['PUT'])
def update_position_route(tour_execution_id):
    return update_position(request, tour_execution_id)

@simulation_routes.route('/end_tour', methods=['POST'])
def end_tour_route():
    return end_tour(request)

@simulation_routes.route('/delete_owned_tour/<int:ownedtours_id>', methods=['DELETE'])
def delete_owned_tour_route(ownedtours_id):
    return delete_owned_tour(request, ownedtours_id)

@simulation_routes.route('/mark_checkpoint_as_reached', methods=['POST'])
def mark_checkpoint_as_reached_route():
    return mark_checkpoint_as_reached(request)