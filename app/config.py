import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/donation_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    
    # Redis Config
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    
    # Razorpay Config
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_jyy9CzFqyj9Tmc')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'uBHGw2fxOEVRLnx92J0eW1AM')
    
    # Base URL for callbacks
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Razorpay Payment Link Settings
    RAZORPAY_PAYMENT_LINK_EXPIRY = 24  # hours
    RAZORPAY_CURRENCY = 'INR'
    RAZORPAY_PAYMENT_CAPTURE = 1  # Auto capture payment
    
    # Razorpay Webhook Settings
    RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', 'your-webhook-secret')
    
    # Payment Callback URLs
    PAYMENT_SUCCESS_URL = '/donation/success'
    PAYMENT_FAILURE_URL = '/donation/failure'
    PAYMENT_CALLBACK_URL = '/payment-callback' 