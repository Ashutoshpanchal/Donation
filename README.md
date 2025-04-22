# Donation Application

A Flask-based web application for managing donations with phone number authentication, Redis-based OTP verification, and Razorpay payment integration.

## Features

- Phone number-based authentication with OTP verification
- JWT-based secure API access
- Donation management system with Razorpay payment links
- Payment status tracking and verification
- Swagger UI documentation
- Docker-based deployment
- PostgreSQL database
- Redis for OTP storage

## Prerequisites

- Docker
- Docker Compose
- Python 3.8 or higher (for local development)
- Razorpay account and API keys

## Project Structure

```
donation/
├── app/
│   ├── auth/           # Authentication related code
│   ├── donations/      # Donation management
│   │   ├── routes.py   # API endpoints
│   │   └── payment.py  # Razorpay integration
│   ├── models/         # Database models
│   ├── __init__.py    # Application initialization
│   └── config.py      # Configuration settings
├── migrations/         # Database migrations
├── docker-compose.yml  # Docker configuration
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd donation
```

2. Configure Razorpay credentials in docker-compose.yml:
```yaml
environment:
  - RAZORPAY_KEY_ID=your_key_id
  - RAZORPAY_KEY_SECRET=your_key_secret
```

3. Start the application using Docker Compose:
```bash
docker-compose up -d
```

The application will be available at:
- API: http://localhost:6060
- Swagger UI: http://localhost:6060/swagger

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user and request OTP
- `POST /auth/verify` - Verify OTP and get access token
- `GET /auth/profile` - Get user profile (requires authentication)
- `PUT /auth/profile` - Update user profile (requires authentication)

### Donations

- `GET /donations` - List all donations created by the user (requires authentication)
- `POST /donations` - Create a new donation link (requires authentication)
- `GET /donations/{id}` - Get donation details (requires authentication)
- `GET /donations/status/{payment_link_id}` - Check donation payment status (requires authentication)
- `DELETE /donations/{id}` - Delete a donation (requires authentication)

## Payment Flow

1. Create a donation link:
```bash
curl -X 'POST' \
  'http://localhost:6060/donations' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "amount": 5000,
    "description": "Test donation",
    "donor_name": "John Doe",
    "donor_email": "john@example.com"
  }'
```

Response:
```json
{
  "message": "Donation link created successfully",
  "donation": {
    "id": 1,
    "amount": 5000,
    "description": "Test donation",
    "status": "link_created",
    "payment_link_id": "plink_123456",
    "payment_link_url": "https://rzp.io/i/abc123",
    "payment_link_expiry": "2024-04-23T10:00:00Z",
    "reference_id": "don_1234567890"
  },
  "payment_link": {
    "url": "https://rzp.io/i/abc123",
    "id": "plink_123456",
    "expiry": "2024-04-23T10:00:00Z"
  }
}
```

2. Check payment status:
```bash
curl -X 'GET' \
  'http://localhost:6060/donations/status/plink_123456' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

Response:
```json
{
  "donation_id": 1,
  "amount": 5000,
  "status": "payment_completed",
  "created_at": "2024-04-22T10:00:00Z",
  "expiry": "2024-04-23T10:00:00Z",
  "donor_name": "John Doe",
  "donor_email": "john@example.com",
  "payment_date": "2024-04-22T10:30:00Z",
  "payment_link_url": "https://rzp.io/i/abc123",
  "razorpay_status": "paid",
  "razorpay_payment_id": "pay_123456"
}
```

## Development

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export FLASK_APP=app
export FLASK_ENV=development
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/donation
export REDIS_URL=redis://localhost:6379/0
export RAZORPAY_KEY_ID=your_key_id
export RAZORPAY_KEY_SECRET=your_key_secret
```

4. Run the application:
```bash
flask run
```

### Database Migrations

To create a new migration:
```bash
flask db migrate -m "description of changes"
```

To apply migrations:
```bash
flask db upgrade
```

## Environment Variables

- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `RAZORPAY_KEY_ID`: Razorpay API key ID
- `RAZORPAY_KEY_SECRET`: Razorpay API key secret

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.


rzp_test_jyy9CzFqyj9Tmc
YWp5aO7C3D1C1rbRGDNkkEYd