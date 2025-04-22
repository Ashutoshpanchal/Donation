from datetime import datetime
from app import db

class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    link_creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='link_created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Payment Link fields
    payment_link_id = db.Column(db.String(100), nullable=True)
    payment_link_url = db.Column(db.String(500), nullable=True)
    payment_link_expiry = db.Column(db.DateTime, nullable=True)
    
    # Donor fields
    donor_name = db.Column(db.String(100), nullable=True, default=None)
    donor_email = db.Column(db.String(100), nullable=True, default=None)
    
    # Payment tracking
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    reference_id = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<Donation {self.id} - {self.amount}>'






    """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NTMzNTk0MSwianRpIjoiNjljYjA0ZjctMzBjMC00ZDc0LTk0M2EtNzljYzJkYjM0OTU5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3NDUzMzU5NDEsImV4cCI6MTc0NTMzOTU0MX0.nXlr-BytIylBUMLPZutrBYn-bQBTokvZGbXLOmHxwJU"""