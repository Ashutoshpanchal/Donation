from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restx import Resource, Namespace, fields
import logging

from app import db, api
from app.auth import bp
from app.models.user import User
from app.auth.utils import send_otp, verify_otp

# Create namespace for auth
ns = Namespace('auth', description='Authentication operations')

# Define models for Swagger documentation
register_model = api.model('Register', {
    'phone_number': fields.String(required=True, description='User phone number')
})

verify_model = api.model('Verify', {
    'phone_number': fields.String(required=True, description='User phone number'),
    'otp': fields.String(required=True, description='OTP received via SMS')
})

profile_model = api.model('Profile', {
    'name': fields.String(description='User name'),
    'email': fields.String(description='User email')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'phone_number': fields.String(description='User phone number'),
    'name': fields.String(description='User name'),
    'email': fields.String(description='User email'),
    'created_at': fields.DateTime(description='Account creation date')
})

@ns.route('/register')
class Register(Resource):
    @ns.expect(register_model)
    @ns.response(200, 'OTP sent successfully')
    @ns.response(400, 'Invalid input')
    def post(self):
        """Register a new user or request OTP for existing user"""
        data = request.json
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return {'error': 'Phone number is required'}, 400
        
        # Check if user already exists
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            # Create new user
            user = User(phone_number=phone_number)
            db.session.add(user)
            db.session.commit()
        
        # Send OTP for verification
        result = send_otp(phone_number)
        if result['success']:
            return {'message': result['message']}, 200
        else:
            return {'error': result['error']}, 400

@ns.route('/verify')
class Verify(Resource):
    @ns.expect(verify_model)
    @ns.response(200, 'Authentication successful')
    @ns.response(400, 'Invalid input')
    def post(self):
        """Verify OTP and authenticate user"""
        data = request.json
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        if not phone_number or not otp:
            return {'error': 'Phone number and OTP are required'}, 400
        
        # Verify OTP
        result = verify_otp(phone_number, otp)
        
        if result['success']:
            # Get or create user
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                user = User(phone_number=phone_number)
                db.session.add(user)
                db.session.commit()
            
            # Create access token with user_id as string
            access_token = create_access_token(identity=str(user.id))
            logging.info(f"Created access token for user_id: {user.id}")
            
            return {
                'message': 'Authentication successful',
                'access_token': access_token,
                'user_id': user.id
            }, 200
        else:
            return {'error': result['error']}, 400

@ns.route('/profile')
class Profile(Resource):
    @ns.doc(security='Bearer')
    @ns.response(200, 'Success', user_model)
    @ns.response(404, 'User not found')
    @jwt_required()
    def get(self):
        """Get user profile"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Getting profile for user_id: {user_id}")
            user = User.query.get(int(user_id))
            
            if not user:
                return {'error': 'User not found'}, 404
            
            return {
                'id': user.id,
                'phone_number': user.phone_number,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }, 200
        except Exception as e:
            logging.error(f"Error getting profile: {str(e)}")
            return {'error': str(e)}, 500

    @ns.doc(security='Bearer')
    @ns.expect(profile_model)
    @ns.response(200, 'Profile updated successfully')
    @ns.response(404, 'User not found')
    @jwt_required()
    def put(self):
        """Update user profile"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Updating profile for user_id: {user_id}")
            user = User.query.get(int(user_id))
            
            if not user:
                return {'error': 'User not found'}, 404
            
            data = request.json
            
            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                user.email = data['email']
            
            db.session.commit()
            
            return {
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'phone_number': user.phone_number,
                    'name': user.name,
                    'email': user.email
                }
            }, 200
        except Exception as e:
            logging.error(f"Error updating profile: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500

# Register the namespace with the blueprint
api.add_namespace(ns) 