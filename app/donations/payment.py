import razorpay
import hmac
import hashlib
from flask import current_app
import logging
from datetime import datetime, timedelta

def create_razorpay_client():
    """Create and return a Razorpay client instance"""
    return razorpay.Client(
        auth=(current_app.config['RAZORPAY_KEY_ID'], 
              current_app.config['RAZORPAY_KEY_SECRET'])
    )

def create_order(amount, currency='INR'):
    """
    Create a Razorpay order
    amount: Amount in paise (multiply by 100 for INR)
    """
    try:
        client = create_razorpay_client()
        data = {
            'amount': int(amount),  # Convert to paise
            'currency': currency,
            'payment_capture': 1  # Auto capture payment
        }
        order = client.order.create(data=data)
        logging.info(f"Created Razorpay order: {order}")
        return order
    except Exception as e:
        logging.error(f"Error creating Razorpay order: {str(e)}")
        raise

def fetch_payment_details(payment_link_id):
    """
    Fetch payment details from Razorpay
    Returns payment status and details
    """
    client = create_razorpay_client()
    try:
        # First try to fetch payment link details
        payment_link = client.payment_link.fetch(payment_link_id)
        logging.info(f"Payment link details: {payment_link}")

        # If payment is completed, fetch the payment details
        if payment_link.get('status') == 'paid':
            payment_id = payment_link.get('payments', [{}])[0].get('id')
            if payment_id:
                payment = client.payment.fetch(payment_id)
                logging.info(f"Payment details: {payment}")
                return {
                    'status': 'paid',
                    'payment': payment,
                    'amount': payment.get('amount', 0),
                    'currency': payment.get('currency'),
                    'created_at': payment.get('created_at'),
                    'id': payment.get('id'),
                    'order_id': payment.get('order_id')
                }
        
        # Return payment link details if payment is not completed
        return {
            'status': payment_link.get('status', 'unknown'),
            'payment': payment_link,
            'amount': payment_link.get('amount', 0),
            'currency': payment_link.get('currency'),
            'created_at': payment_link.get('created_at'),
            'id': payment_link.get('id'),
            'order_id': payment_link.get('reference_id')
        }

    except Exception as e:
        logging.error(f"Error fetching payment details: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def create_payment_link(amount, name, email, description="Donation via Localhost"):
    """
    Create a Razorpay payment link
    """
    client = create_razorpay_client()
    data = {
        "amount": int(amount * 100),  # Convert to paise
        "currency": "INR",
        "customer": {
            "name": name,
            "email": email
        },
        "description": description,
        "callback_url": f"{current_app.config.get('BASE_URL', 'http://localhost:6060')}/donations/callback",
        "callback_method": "get",
        "expire_by": int((datetime.now() + timedelta(hours=24)).timestamp()),
        "notify": {
            "sms": True,
            "email": True
        },
        "reminder_enable": True,
        "notes": {
            "donation_type": "general",
            "platform": "web"
        },
        "reference_id": f"don_{int(datetime.now().timestamp())}"
    }
    payment_link = client.payment_link.create(data=data)
    logging.info(f"Created payment link: {payment_link}")
    return payment_link 