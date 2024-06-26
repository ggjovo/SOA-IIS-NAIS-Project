from flask import Flask, request
from flask_cors import CORS
from routes import tour_routes, cart_routes, simulation_routes

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)  # Only allow requests from http://localhost:3000

@app.before_request
def handle_options_requests():
    if request.method == 'OPTIONS':
        response = app.make_response('')
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


if __name__ == '__main__':
    app.register_blueprint(tour_routes)
    app.register_blueprint(cart_routes)
    app.register_blueprint(simulation_routes)
    app.run(host='0.0.0.0', port=8084)
