from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes with all origins (for development)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    from routes import api
    app.register_blueprint(api)
    
    return app


if __name__ == '__main__':
    app = create_app()

    app.run(debug=True, port=5000, host="0.0.0.0")