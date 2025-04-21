# Donation Application

A Flask-based web application for managing donations with phone number authentication and Redis-based OTP verification.

## Features

- Phone number-based authentication with OTP verification
- JWT-based secure API access
- Donation management system
- Swagger UI documentation
- Docker-based deployment
- PostgreSQL database
- Redis for OTP storage

## Prerequisites

- Docker
- Docker Compose
- Python 3.8 or higher (for local development)

## Project Structure

```
donation/
├── app/
│   ├── auth/           # Authentication related code
│   ├── donations/      # Donation management
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

2. Start the application using Docker Compose:
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

- `GET /donations` - List all donations (requires authentication)
- `POST /donations` - Create a new donation (requires authentication)
- `GET /donations/{id}` - Get donation details (requires authentication)
- `PUT /donations/{id}` - Update donation status (requires authentication)

## Authentication Flow

1. Register with phone number:
```bash
curl -X 'POST' \
  'http://localhost:6060/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "phone_number": "+1234567890"
  }'
```

2. Verify OTP:
```bash
curl -X 'POST' \
  'http://localhost:6060/auth/verify' \
  -H 'Content-Type: application/json' \
  -d '{
    "phone_number": "+1234567890",
    "otp": "123456"
  }'
```

3. Use the received token for authenticated requests:
```bash
curl -X 'GET' \
  'http://localhost:6060/donations' \
  -H 'Authorization: Bearer YOUR_TOKEN'
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 