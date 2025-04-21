from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_restx import Resource, Namespace, fields
import logging

from app import db, api
from app.models.donation import Donation
from app.models.user import User

# Create namespace for donations
ns = Namespace('donations', description='Donation operations')

# Define models for Swagger documentation
donation_model = api.model('Donation', {
    'id': fields.Integer(description='Donation ID'),
    'user_id': fields.Integer(description='User ID'),
    'amount': fields.Float(description='Donation amount'),
    'description': fields.String(description='Donation description'),
    'status': fields.String(description='Donation status'),
    'created_at': fields.DateTime(description='Donation creation date')
})

create_donation_model = api.model('CreateDonation', {
    'amount': fields.Float(required=True, description='Donation amount'),
    'description': fields.String(description='Donation description')
})

@ns.route('')
class DonationList(Resource):
    @ns.doc(security='Bearer')
    @ns.response(200, 'Success', [donation_model])
    @jwt_required()
    def get(self):
        """Get all donations for the current user"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Getting donations for user_id: {user_id}")
            donations = Donation.query.filter_by(user_id=user_id).all()
            
            return [{
                'id': donation.id,
                'user_id': donation.user_id,
                'amount': donation.amount,
                'description': donation.description,
                'status': donation.status,
                'created_at': donation.created_at.isoformat()
            } for donation in donations], 200
        except Exception as e:
            logging.error(f"Error getting donations: {str(e)}")
            return {'error': str(e)}, 500

    @ns.doc(security='Bearer')
    @ns.expect(create_donation_model)
    @ns.response(201, 'Donation created successfully')
    @ns.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        """Create a new donation"""
        try:
            # Verify JWT token first
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            logging.info(f"Creating donation for user_id: {user_id}")
            
            # Check if user exists
            user = User.query.get(user_id)
            if not user:
                logging.error(f"User not found with id: {user_id}")
                return {'error': 'User not found'}, 404
            
            data = request.json
            logging.info(f"Request data: {data}")
            
            if not data.get('amount') or not isinstance(data['amount'], (int, float)):
                return {'error': 'Valid amount is required'}, 400
            
            donation = Donation(
                user_id=user_id,
                amount=data['amount'],
                description=data.get('description', ''),
                status='pending'
            )
            
            db.session.add(donation)
            db.session.commit()
            logging.info(f"Donation created successfully with id: {donation.id}")
            
            return {
                'message': 'Donation created successfully',
                'donation': {
                    'id': donation.id,
                    'amount': donation.amount,
                    'description': donation.description,
                    'status': donation.status
                }
            }, 201
        except Exception as e:
            logging.error(f"Error creating donation: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500

@ns.route('/<int:donation_id>')
class DonationResource(Resource):
    @ns.doc(security='Bearer')
    @ns.response(200, 'Success', donation_model)
    @ns.response(404, 'Donation not found')
    @jwt_required()
    def get(self, donation_id):
        """Get a specific donation"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Getting donation {donation_id} for user_id: {user_id}")
            donation = Donation.query.filter_by(id=donation_id, user_id=user_id).first()
            
            if not donation:
                return {'error': 'Donation not found'}, 404
            
            return {
                'id': donation.id,
                'user_id': donation.user_id,
                'amount': donation.amount,
                'description': donation.description,
                'status': donation.status,
                'created_at': donation.created_at.isoformat()
            }, 200
        except Exception as e:
            logging.error(f"Error getting donation: {str(e)}")
            return {'error': str(e)}, 500

    @ns.doc(security='Bearer')
    @ns.expect(create_donation_model)
    @ns.response(200, 'Donation updated successfully')
    @ns.response(404, 'Donation not found')
    @jwt_required()
    def put(self, donation_id):
        """Update a donation"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Updating donation {donation_id} for user_id: {user_id}")
            donation = Donation.query.filter_by(id=donation_id, user_id=user_id).first()
            
            if not donation:
                return {'error': 'Donation not found'}, 404
            
            data = request.json
            
            if 'amount' in data:
                if not isinstance(data['amount'], (int, float)):
                    return {'error': 'Valid amount is required'}, 400
                donation.amount = data['amount']
            
            if 'description' in data:
                donation.description = data['description']
            
            if 'status' in data:
                donation.status = data['status']
            
            db.session.commit()
            
            return {
                'message': 'Donation updated successfully',
                'donation': {
                    'id': donation.id,
                    'amount': donation.amount,
                    'description': donation.description,
                    'status': donation.status
                }
            }, 200
        except Exception as e:
            logging.error(f"Error updating donation: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500

    @ns.doc(security='Bearer')
    @ns.response(200, 'Donation deleted successfully')
    @ns.response(404, 'Donation not found')
    @jwt_required()
    def delete(self, donation_id):
        """Delete a donation"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Deleting donation {donation_id} for user_id: {user_id}")
            donation = Donation.query.filter_by(id=donation_id, user_id=user_id).first()
            
            if not donation:
                return {'error': 'Donation not found'}, 404
            
            db.session.delete(donation)
            db.session.commit()
            
            return {'message': 'Donation deleted successfully'}, 200
        except Exception as e:
            logging.error(f"Error deleting donation: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500

# Register the namespace with the blueprint
api.add_namespace(ns) 