from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restx import Api
import redis
import os
import logging

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api(
    title='Donation System API',
    version='1.0',
    description='A donation system API with phone number authentication and payment processing',
    doc='/swagger',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    },
    security='Bearer'
)

# Configure Redis connection
redis_client = redis.Redis(
    host='redis',  # Use the service name from docker-compose
    port=6379,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5
)
# Test the connection
redis_client.ping()
logging.info("Successfully connected to Redis")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'KEEPITSERCET')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    api.init_app(app)

    # Add JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            'msg': 'Missing Authorization Header'
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(callback):
        return jsonify({
            'msg': 'Token has expired'
        }), 401

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.donations import bp as donations_bp
    app.register_blueprint(donations_bp)

    @app.route('/health')
    def health_check():
        try:
            redis_client.ping()
            return {'status': 'healthy', 'redis': 'connected'}
        except redis.ConnectionError:
            return {'status': 'unhealthy', 'redis': 'disconnected'}

    return app 