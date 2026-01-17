# Currency Exchange API

A Django REST Framework application that provides currency exchange rate information with user balance management and exchange history tracking.

## Features

- User registration and JWT authentication
- Currency exchange rate lookup (using ExchangeRate API)
- User balance management (each request costs 1 credit)
- Exchange history with filtering capabilities
- Swagger/ReDoc API documentation

## Technology Stack

- Python 3.13
- Django 6.0
- Django REST Framework
- PostgreSQL 16
- Docker & Docker Compose
- JWT Authentication (Simple JWT)
- Pytest for testing

## Prerequisites

- Docker and Docker Compose installed
- ExchangeRate API key (get one at https://www.exchangerate-api.com/)

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/danil25-stack/globaldev
cd globaldev
```

### 2. Configure environment variables

Copy the example environment file and update it with your values:

```bash
cp .env.example .env
```

Edit `.env` file and set your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# API Keys
EXCHANGE_RATE_API_KEY=your-exchange-rate-api-key-here
```

### 3. Build and run with Docker Compose

```bash
docker-compose up --build
```

The application will be available at: `http://localhost:8000`

### 4. Create a superuser

In a new terminal, run:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Running Tests

To run the test suite with pytest:

```bash
docker-compose exec web pytest
```

For verbose output:

```bash
docker-compose exec web pytest -v
```

## API Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

## API Endpoints

### Authentication

#### Register a new user
- **URL**: `POST /api/v1/users/register/`
- **Authentication**: None required
- **Request Body**:
```json
{
  "username": "testuser",
  "password": "securepassword123"
}
```
- **Response** (201 Created):
```json
{
  "username": "testuser"
}
```

#### Obtain JWT Token
- **URL**: `POST /api/v1/auth/jwt/create/`
- **Authentication**: None required
- **Request Body**:
```json
{
  "username": "testuser",
  "password": "securepassword123"
}
```
- **Response** (200 OK):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Refresh JWT Token
- **URL**: `POST /api/v1/auth/jwt/refresh/`
- **Authentication**: None required
- **Request Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
- **Response** (200 OK):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### User Balance

#### Get current balance
- **URL**: `GET /api/v1/users/balance/`
- **Authentication**: Required (JWT)
- **Headers**:
```
Authorization: Bearer <your-access-token>
```
- **Response** (200 OK):
```json
{
  "balance": 1000
}
```

### Currency Exchange

#### Get exchange rate
- **URL**: `POST /api/v1/exchange/currency/`
- **Authentication**: Required (JWT)
- **Headers**:
```
Authorization: Bearer <your-access-token>
```
- **Request Body**:
```json
{
  "currency_code": "USD"
}
```
- **Response** (200 OK):
```json
{
  "currency_code": "USD",
  "rate_to_uah": "41.234567",
  "cost": 1,
  "balance_left": "999.00"
}
```
- **Error Response** (402 Payment Required):
```json
{
  "detail": "Insufficient balance for this exchange."
}
```
- **Error Response** (400 Bad Request):
```json
{
  "currency_code": [
    "currency_code must be 3 letters, like 'USD'"
  ]
}
```
- **Error Response** (502 Bad Gateway):
```json
{
  "detail": "ExchangeRate API request failed: ..."
}
```

#### Get exchange history
- **URL**: `GET /api/v1/exchange/history/`
- **Authentication**: Required (JWT)
- **Headers**:
```
Authorization: Bearer <your-access-token>
```
- **Query Parameters** (optional):
  - `currency_code`: Filter by currency code (e.g., `?currency_code=USD`)
  - `created_at_after`: Filter by date after (e.g., `?created_at_after=2025-01-01`)
  - `created_at_before`: Filter by date before (e.g., `?created_at_before=2025-12-31`)
- **Response** (200 OK):
```json
[
  {
    "id": 1,
    "currency_code": "USD",
    "rate": "41.23456700",
    "created_at": "2025-01-17T10:30:00Z"
  },
  {
    "id": 2,
    "currency_code": "EUR",
    "rate": "45.67890100",
    "created_at": "2025-01-17T09:15:00Z"
  }
]
```

## Authorization Header Format

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```


## Project Structure

```
globaldev/
├── core/                   # Django project settings
│   ├── settings.py        # Main settings
│   └── urls.py            # Root URL configuration
├── users/                  # User management app
│   ├── models.py          # UserBalance model
│   ├── views.py           # Registration & balance views
│   ├── serializers.py     # User serializers
│   └── urls.py            # User endpoints
├── exchange/               # Currency exchange app
│   ├── models.py          # CurrencyExchange model
│   ├── views.py           # Currency & history views
│   ├── serializers.py     # Exchange serializers
│   ├── services/          # Business logic
│   │   └── exchange_service.py
│   ├── filters.py         # QuerySet filters
│   ├── tests/             # Test files
│   └── urls.py            # Exchange endpoints
├── docker-compose.yml      # Docker orchestration
├── Dockerfile             # Docker image definition
├── Pipfile                # Python dependencies
└── manage.py              # Django management script
```

## Database Models

### UserBalance
- `user`: OneToOne relationship with User
- `balance`: Integer (default: 1000)

### CurrencyExchange
- `user`: ForeignKey to User
- `currency_code`: CharField (max 10 chars)
- `rate`: DecimalField (18 digits, 8 decimal places)
- `created_at`: DateTimeField (auto-generated)

## Configuration

### JWT Token Lifetimes
- **Access Token**: 15 minutes
- **Refresh Token**: 1 day

### Exchange Rate Service
- **Cost per request**: 1 credit (configurable via `COST_PER_REQUEST` env variable)
- **Initial user balance**: 1000 credits
- **API Provider**: ExchangeRate-API (https://www.exchangerate-api.com/)

## Admin Panel

Access the Django admin panel at: http://localhost:8000/api/v1/admin/

Use the superuser credentials you created earlier.

## Stopping the Application

```bash
docker-compose down
```

To remove volumes as well:

```bash
docker-compose down -v
```

