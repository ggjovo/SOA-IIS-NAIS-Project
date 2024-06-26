from flask import Flask
from flask_cors import CORS
#from following import following_routes
from routes import blog_routes

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)  # Only allow requests from http://localhost:3000


if __name__ == '__main__':
    #app.register_blueprint(following_routes)
    app.register_blueprint(blog_routes)
    app.run(host='0.0.0.0', port=8083)