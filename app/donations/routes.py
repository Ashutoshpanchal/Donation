from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_restx import Resource, Namespace, fields
import logging
from datetime import datetime

from app import db, api
from app.models.donation import Donation
from app.models.user import User
from app.donations.payment import create_payment_link, fetch_payment_details

# Create namespace for donations
ns = Namespace('donations', description='Donation operations')

# Define models for Swagger documentation
donation_model = api.model('Donation', {
    'id': fields.Integer(description='Donation ID'),
    'link_creator_id': fields.Integer(description='Link Creator ID'),
    'amount': fields.Float(description='Donation amount'),
    'description': fields.String(description='Donation description'),
    'status': fields.String(description='Donation status'),
    'created_at': fields.DateTime(description='Donation creation date'),
    'payment_link_id': fields.String(description='Payment Link ID'),
    'payment_link_url': fields.String(description='Payment Link URL'),
    'payment_link_expiry': fields.DateTime(description='Payment Link Expiry'),
    'donor_name': fields.String(description='Donor Name'),
    'donor_email': fields.String(description='Donor Email'),
    'payment_date': fields.DateTime(description='Payment Date'),
    'reference_id': fields.String(description='Reference ID')
})

create_donation_link_model = api.model('CreateDonationLink', {
    'amount': fields.Float(required=True, description='Donation amount'),
    'description': fields.String(description='Donation description'),
    'donor_name': fields.String(description='Name'),
    'donor_email': fields.String(description='Email')
})

@ns.route('')
class DonationList(Resource):
    @ns.doc(security='Bearer')
    @ns.response(200, 'Success', [donation_model])
    @jwt_required()
    def get(self):
        """Get all donations created by the current user"""
        try:
            user_id = get_jwt_identity()
            logging.info(f"Getting donations for user_id: {user_id}")
            donations = Donation.query.filter_by(link_creator_id=user_id).all()
            
            return [{
                'id': donation.id,
                'link_creator_id': donation.link_creator_id,
                'amount': donation.amount,
                'description': donation.description,
                'status': donation.status,
                'created_at': donation.created_at.isoformat(),
                'payment_link_id': donation.payment_link_id,
                'payment_link_url': donation.payment_link_url,
                'payment_link_expiry': donation.payment_link_expiry.isoformat() if donation.payment_link_expiry else None,
                'donor_name': donation.donor_name,
                'donor_email': donation.donor_email,
                'payment_date': donation.payment_date.isoformat() if donation.payment_date else None,
                'reference_id': donation.reference_id
            } for donation in donations], 200
        except Exception as e:
            logging.error(f"Error getting donations: {str(e)}")
            return {'error': str(e)}, 500

    @ns.doc(security='Bearer')
    @ns.expect(create_donation_link_model)
    @ns.response(201, 'Donation link created successfully')
    @ns.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        """Create a new donation link"""
        try:
            data = request.get_json()
            amount = data.get('amount')
            description = data.get('description', 'Donation via Localhost')
            donor_name = data.get('donor_name','')
            donor_email = data.get('donor_email','')
            # Validate amount
            if not isinstance(amount, (int, float)) or amount <= 0:
                return {'message': 'Invalid amount. Amount must be a positive number'}, 400

            # Get current user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return {'message': 'User not found'}, 404

            # Create payment link
            payment_link = create_payment_link(
                amount=amount,
                name=user.name,
                email=user.email,
                description=description
            )

            # Create donation record
            donation = Donation(
                link_creator_id=user_id,
                amount=amount,
                description=description,
                status='link_created',
                payment_link_id=payment_link['id'],
                payment_link_url=payment_link['short_url'],
                payment_link_expiry=datetime.fromtimestamp(payment_link['expire_by']),
                reference_id=payment_link['reference_id'],
                donor_name=donor_name,
                donor_email=donor_email
            )

            # Add donation to database
            db.session.add(donation)
            db.session.commit()

            # Log successful creation
            logging.info(f"Created donation link with ID {donation.id} and payment link {payment_link['id']}")

            return {
                'message': 'Donation link created successfully',
                'donation': {
                    'id': donation.id,
                    'amount': donation.amount,
                    'description': donation.description,
                    'status': donation.status,
                    'created_at': donation.created_at.isoformat(),
                    'payment_link_id': donation.payment_link_id,
                    'payment_link_url': donation.payment_link_url,
                    'payment_link_expiry': donation.payment_link_expiry.isoformat(),
                    'reference_id': donation.reference_id,
                    'donor_name': None,
                    'donor_email': None
                },
                'payment_link': {
                    'url': payment_link['short_url'],
                    'id': payment_link['id'],
                    'expiry': datetime.fromtimestamp(payment_link['expire_by']).isoformat()
                }
            }, 201

        except Exception as e:
            logging.error(f"Error creating donation link: {str(e)}")
            db.session.rollback()
            return {'message': 'Error creating donation link', 'error': str(e)}, 500

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
            donation = Donation.query.filter_by(id=donation_id, link_creator_id=user_id).first()
            
            if not donation:
                return {'error': 'Donation not found'}, 404
            
            return {
                'id': donation.id,
                'link_creator_id': donation.link_creator_id,
                'amount': donation.amount,
                'description': donation.description,
                'status': donation.status,
                'created_at': donation.created_at.isoformat(),
                'payment_link_id': donation.payment_link_id,
                'payment_link_url': donation.payment_link_url,
                'payment_link_expiry': donation.payment_link_expiry.isoformat() if donation.payment_link_expiry else None,
                'donor_name': donation.donor_name,
                'donor_email': donation.donor_email,
                'payment_date': donation.payment_date.isoformat() if donation.payment_date else None,
                'reference_id': donation.reference_id
            }, 200
        except Exception as e:
            logging.error(f"Error getting donation: {str(e)}")
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
            donation = Donation.query.filter_by(id=donation_id, link_creator_id=user_id).first()
            
            if not donation:
                return {'error': 'Donation not found'}, 404
            
            db.session.delete(donation)
            db.session.commit()
            
            return {'message': 'Donation deleted successfully'}, 200
        except Exception as e:
            logging.error(f"Error deleting donation: {str(e)}")
            db.session.rollback()
            return {'error': str(e)}, 500

@ns.route('/status/<string:payment_link_id>')
class DonationStatus(Resource):
    @ns.doc(security='Bearer')
    @ns.response(200, 'Success')
    @ns.response(404, 'Donation not found')
    @jwt_required()
    def get(self, payment_link_id):
        """Get donation status by payment link ID"""
        try:
            # First find the donation
            donation = Donation.query.filter_by(
                payment_link_id=payment_link_id,
                link_creator_id=get_jwt_identity()
            ).first()

            if not donation:
                return {'message': 'Donation not found'}, 404

            # Fetch payment details from Razorpay
            payment_details = fetch_payment_details(payment_link_id)
            logging.info(f"Payment details from Razorpay: {payment_details}")

            # Update donation status based on Razorpay response
            if payment_details.get('status') == 'paid':
                donation.status = 'payment_completed'
                donation.payment_date = datetime.fromtimestamp(payment_details.get('created_at', 0))
                donation.razorpay_payment_id = payment_details.get('id')
            elif payment_details.get('status') == 'created':
                donation.status = 'link_created'
            else:
                donation.status = 'payment_failed'

            # Save changes to database
            db.session.commit()

            return {
                'donation_id': donation.id,
                'amount': donation.amount,
                'status': donation.status,
                'created_at': donation.created_at.isoformat(),
                'expiry': donation.payment_link_expiry.isoformat() if donation.payment_link_expiry else None,
                'donor_name': donation.donor_name,
                'donor_email': donation.donor_email,
                'payment_date': donation.payment_date.isoformat() if donation.payment_date else None,
                'payment_link_url': donation.payment_link_url,
                'razorpay_status': payment_details.get('status'),
                'razorpay_payment_id': payment_details.get('id')
            }, 200

        except Exception as e:
            logging.error(f"Error fetching donation status: {str(e)}")
            return {'message': 'Error fetching donation status', 'error': str(e)}, 500


# Register the namespace with the blueprint
api.add_namespace(ns) 