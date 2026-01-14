# MarketLink Multi-Vendor Marketplace

A Django + Django REST Framework backend for MarketLink, a multi-vendor marketplace connecting vehicle owners with local repair shops. Supports vendors, variant-priced services, repair orders, mocked payments, and idempotent webhook-based order status updates. Designed with concurrency and realistic business rules in mind.

## Features

- **Custom User Model**: AbstractBaseUser with roles (customer, vendor, admin)
- **Vendor Management**: Profiles, services, and service variants with pricing
- **Order Management**: UUID-based orders with status tracking
- **Concurrency Safety**: Redis-based stock management to prevent double-booking
- **Payment Integration**: Mocked payment flow with webhook handling
- **Background Tasks**: Celery for asynchronous order processing
- **API Authentication**: DRF Token authentication

## Tech Stack

- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MarketLink-multi-vendor-marketplace
   ```

2. **Create virtual environment**
   ```bash
   python -m venv Env
   Env\Scripts\activate  # On Windows
   # source Env/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=marketlink
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_URL=redis://localhost:6379/0
   WEBHOOK_SECRET=your-webhook-secret-here
   ```

5. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb marketlink

   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis server**
   ```bash
   # Install Redis and start service
   redis-server
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Run Celery worker (in separate terminal)**
   ```bash
   celery -A marketlink worker --loglevel=info
   ```

## API Endpoints

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `GET /api/users/profile/` - Get user profile

### Vendors
- `GET/POST /api/vendors/profiles/` - Vendor profiles
- `GET/POST /api/vendors/services/` - Services
- `GET/POST /api/vendors/variants/` - Service variants

### Orders
- `GET/POST /api/orders/` - Repair orders
- `POST /api/orders/{id}/initiate_payment/` - Initiate payment
- `POST /api/orders/webhooks/payment/` - Payment webhook

## Design Decisions

### Concurrency & Stock Management
- **Redis Locks**: Used Redis distributed locks to prevent race conditions during stock decrement
- **Atomic Transactions**: Database transactions ensure data consistency
- **Stock Validation**: Check stock availability before creating orders

### Payment Flow
- **Mocked Payments**: Simulated payment gateway for development
- **Webhook Idempotency**: Redis-based event deduplication using `event_id`
- **Signature Validation**: HMAC-SHA256 signature verification for webhook security

### Authentication
- **DRF Token Auth**: Simple token-based authentication (JWT could be swapped in)
- **Role-Based Access**: Custom user model with roles for different permissions

### Background Tasks
- **Celery**: Asynchronous task processing for order fulfillment
- **Redis Broker**: Lightweight message broker for task queuing

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test vendors
python manage.py test orders

# Run with coverage
pip install coverage
coverage run manage.py test
coverage report
```

## Project Structure

```
marketlink/
├── users/           # User management app
├── vendors/         # Vendor and service management
├── orders/          # Order processing and payments
├── marketlink/      # Project settings
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
