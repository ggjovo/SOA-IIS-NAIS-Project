import logging
from flask import Flask
from flask_cors import CORS
from routes import gateway_routes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

if __name__ == '__main__':
    app.register_blueprint(gateway_routes, url_prefix='/api')
    app.run(host='0.0.0.0', port=8088, debug=True)
