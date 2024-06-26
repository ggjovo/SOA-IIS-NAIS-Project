from flask import Flask
from flask_cors import CORS
from routes import recommender_routes

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)  # Only allow requests from http://localhost:3000


if __name__ == '__main__':
    #app.register_blueprint(following_routes)
    app.register_blueprint(recommender_routes)
    app.run(host='0.0.0.0', port=8085)