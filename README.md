# MarketLink Multi-Vendor Marketplace

A comprehensive Django + Django REST Framework backend for MarketLink, a multi-vendor marketplace connecting vehicle owners with local repair shops. Supports vendors, variant-priced services, repair orders, mocked payments, and idempotent webhook-based order status updates. Designed with concurrency safety and realistic business rules in mind.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Models Documentation](#models-documentation)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **🔐 Custom User Model**: AbstractBaseUser with roles (customer, vendor, admin)
- **🏪 Vendor Management**: Profiles, services, and service variants with pricing
- **📋 Order Management**: UUID-based orders with comprehensive status tracking
- **🔒 Concurrency Safety**: Redis-based stock management to prevent double-booking
- **💳 Payment Integration**: Mocked payment flow with webhook handling
- **⚡ Background Tasks**: Celery for asynchronous order processing
- **🔑 API Authentication**: DRF Token authentication
- **🧪 Comprehensive Testing**: 15+ unit tests covering all critical functionality
- **📊 Admin Interface**: Django admin integration for data management

## Tech Stack

- **Backend Framework**: Django 4.2
- **API Framework**: Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache/Broker**: Redis
- **Task Queue**: Celery
- **Authentication**: DRF Token Authentication
- **Environment Management**: python-decouple
- **Testing**: Django Test Framework + DRF APIClient

## Architecture

### Application Structure

The project follows Django's app-based architecture with three main applications:

- **`users`**: Handles user authentication, registration, and profile management
- **`vendors`**: Manages vendor profiles, services, and service variants
- **`orders`**: Handles order creation, payment processing, and status tracking

### Data Flow

1. **User Registration/Login** → Token generation
2. **Vendor Setup** → Create profile, services, variants
3. **Order Creation** → Stock validation → Payment initiation
4. **Payment Processing** → Webhook notification → Order status update
5. **Background Processing** → Invoice generation → Order completion

### Concurrency Handling

- Redis distributed locks prevent race conditions during stock decrement
- Database transactions ensure atomic operations
- Idempotent webhooks prevent duplicate processing

## Project Structure

```
MarketLink-multi-vendor-marketplace/
├── manage.py                           # Django management script
├── marketlink/                         # Main Django project
│   ├── __init__.py
│   ├── asgi.py                         # ASGI configuration
│   ├── celery.py                       # Celery configuration
│   ├── settings.py                     # Project settings
│   ├── urls.py                         # Main URL configuration
│   └── wsgi.py                         # WSGI configuration
├── users/                              # User management app
│   ├── __init__.py
│   ├── admin.py                        # Admin interface
│   ├── apps.py                         # App configuration
│   ├── models.py                       # User models
│   ├── serializers.py                  # DRF serializers
│   ├── tests.py                        # Unit tests
│   ├── urls.py                         # URL patterns
│   ├── views.py                        # API views
│   └── migrations/                     # Database migrations
├── vendors/                            # Vendor management app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                       # Vendor, Service, ServiceVariant models
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── orders/                             # Order processing app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                       # RepairOrder model
│   ├── serializers.py
│   ├── tasks.py                        # Celery tasks
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── db.sqlite3                          # SQLite database (development)
└── README.md                           # This documentation
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL (production) or SQLite (development)
- Redis
- Git

### Quick Start (Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MarketLink-multi-vendor-marketplace
   ```

2. **Create virtual environment**
   ```bash
   python -m venv Env
   # Windows
   Env\Scripts\activate
   # macOS/Linux
   source Env/bin/activate
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
   ```env
   SECRET_KEY=django-insecure-your-secret-key-here
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
   # For SQLite (development - already configured)
   python manage.py migrate

   # For PostgreSQL (production)
   # createdb marketlink
   # python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis server** (in separate terminal)
   ```bash
   redis-server
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Run Celery worker** (in separate terminal)
   ```bash
   celery -A marketlink worker --loglevel=info
   ```

### Production Setup

For production deployment, update the database configuration in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/users/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123",
    "role": "customer"
}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "role": "customer"
    },
    "token": "abc123def456..."
}
```

#### Login User
```http
POST /api/users/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "role": "customer"
    },
    "token": "abc123def456..."
}
```

### Vendor Endpoints

#### Create Vendor Profile
```http
POST /api/vendors/profiles/
Authorization: Token abc123def456...
Content-Type: application/json

{
    "business_name": "AutoFix Garage",
    "address": "123 Main St, City, State"
}
```

#### Create Service
```http
POST /api/vendors/services/
Authorization: Token abc123def456...
Content-Type: application/json

{
    "name": "Oil Change",
    "description": "Complete oil change service"
}
```

#### Create Service Variant
```http
POST /api/vendors/variants/
Authorization: Token abc123def456...
Content-Type: application/json

{
    "service": 1,
    "price": 49.99,
    "estimated_minutes": 30,
    "stock": 10
}
```

### Order Endpoints

#### Create Repair Order
```http
POST /api/orders/
Authorization: Token abc123def456...
Content-Type: application/json

{
    "variant": 1
}
```

**Response:**
```json
{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "total_amount": 49.99,
    "payment_url": "https://payment-gateway.com/pay/123",
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### Payment Webhook
```http
POST /webhooks/payment/
Content-Type: application/json
X-Webhook-Signature: sha256=abc123...

{
    "event_id": "evt_123456",
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 49.99,
    "status": "paid",
    "timestamp": "2024-01-15T10:35:00Z"
}
```

## Models Documentation

### User Model (`users/models.py`)

```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)          # Unique email address
    name = models.CharField(max_length=255)         # Full name
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)   # Account active status
    is_staff = models.BooleanField(default=False)   # Django admin access
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
```

### Vendor Models (`vendors/models.py`)

```python
class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Service(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ServiceVariant(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_minutes = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Order Model (`orders/models.py`)

```python
class RepairOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Testing

### Running Tests

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
coverage html  # Generate HTML report
```

### Test Coverage

The test suite includes 15+ tests covering:

#### Users App (`users/tests.py`)
- User registration with valid/invalid data
- User login with correct/incorrect credentials
- Token authentication
- Profile retrieval

#### Vendors App (`vendors/tests.py`)
- Vendor profile creation and management
- Service creation and CRUD operations
- Service variant creation with stock management
- Stock decrement concurrency testing

#### Orders App (`orders/tests.py`)
- Order creation with stock validation
- Payment webhook processing
- Idempotency handling
- Order status updates
- Background task execution

### Test Structure

Each test class follows Django's testing patterns:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Test data setup

    def test_order_creation(self):
        # Test implementation
        pass
```

## Design Decisions

### Concurrency & Stock Management

**Problem**: Multiple users could simultaneously book the last available service slot, causing overbooking.

**Solution**:
- **Redis Distributed Locks**: Acquire lock before stock decrement
- **Atomic Transactions**: Database-level atomicity for stock updates
- **Optimistic Locking**: Version-based concurrency control

```python
# Example from orders/views.py
import redis
from django.conf import settings

redis_client = redis.from_url(settings.REDIS_URL)

def create_order(request):
    variant = ServiceVariant.objects.get(id=request.data['variant'])

    # Acquire Redis lock
    lock_key = f"stock_lock:{variant.id}"
    with redis_client.lock(lock_key, timeout=10):
        if variant.stock > 0:
            # Atomic stock decrement
            variant.stock -= 1
            variant.save()
            # Create order
            order = RepairOrder.objects.create(...)
            return Response({'order_id': order.order_id})
        else:
            return Response({'error': 'Out of stock'}, status=400)
```

### Payment Flow & Webhook Idempotency

**Problem**: Payment gateways may send duplicate webhook notifications.

**Solution**:
- **Event Deduplication**: Redis-based event ID tracking
- **Signature Validation**: HMAC-SHA256 verification
- **Idempotent Operations**: Safe retry handling

```python
# Example from orders/views.py
import hmac
import hashlib

def payment_webhook(request):
    # Verify signature
    signature = request.headers.get('X-Webhook-Signature')
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return Response({'error': 'Invalid signature'}, status=400)

    # Check idempotency
    event_id = request.data['event_id']
    if redis_client.exists(f"webhook:{event_id}"):
        return Response({'status': 'already_processed'})

    redis_client.setex(f"webhook:{event_id}", 3600, 'processed')

    # Process payment
    order = RepairOrder.objects.get(order_id=request.data['order_id'])
    order.status = 'paid'
    order.save()

    # Trigger background task
    process_order.delay(order.id)

    return Response({'status': 'success'})
```

### Authentication Choice

**Decision**: DRF Token Authentication over JWT

**Rationale**:
- Simpler implementation for MVP
- Sufficient security for initial release
- Easy migration to JWT if needed
- Built-in Django admin integration

### Database Choice

**Development**: SQLite for simplicity
**Production**: PostgreSQL for scalability

**Rationale**:
- SQLite: Zero-configuration, file-based, perfect for development
- PostgreSQL: ACID compliance, advanced features, production-ready

## Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "marketlink.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-production-key
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=marketlink
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password

  redis:
    image: redis:6-alpine

  celery:
    build: .
    command: celery -A marketlink worker --loglevel=info
    depends_on:
      - redis
```

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=marketlink_prod
DB_USER=marketlink_user
DB_PASSWORD=secure_password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
WEBHOOK_SECRET=your-webhook-secret
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
django.db.utils.OperationalError: connection to server failed
```
**Solution**: Ensure PostgreSQL is running and credentials are correct in `.env`

#### 2. Redis Connection Error
```
redis.exceptions.ConnectionError: Connection refused
```
**Solution**: Start Redis server or check REDIS_URL in settings

#### 3. Celery Worker Not Processing Tasks
**Solution**: Ensure Celery worker is running:
```bash
celery -A marketlink worker --loglevel=info
```

#### 4. Webhook Signature Validation Fails
**Solution**: Verify WEBHOOK_SECRET matches between sender and receiver

#### 5. Stock Concurrency Issues
**Solution**: Ensure Redis is running for distributed locks

### Debug Commands

```bash
# Check Django system
python manage.py check

# Verify database connections
python manage.py dbshell

# Test Redis connection
python manage.py shell
>>> import redis
>>> r = redis.from_url('redis://localhost:6379/0')
>>> r.ping()
True

# View Celery tasks
celery -A marketlink inspect active
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**
   ```bash
   python manage.py test
   ```
6. **Check code quality**
   ```bash
   # Install black and flake8
   pip install black flake8
   black .
   flake8 .
   ```
7. **Update documentation** if needed
8. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```
9. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
10. **Create a Pull Request**

### Code Standards

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings to classes and methods
- Write comprehensive unit tests
- Update documentation for API changes

### Commit Message Format

```
Type: Brief description

Detailed explanation if needed

Fixes #issue_number
```

**Types**: `Add`, `Fix`, `Update`, `Remove`, `Refactor`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- **Developer**: MD Rabbi Islam
- **Email**: rabbiprimon00000@gmail.com
- **LinkedIn**: [MD Rabbi Islam](https://www.linkedin.com/in/md-rabbi-islam-747770231/)
- **GitHub**: [RabbiPrimon](https://github.com/RabbiPrimon)

## Support

For support, email rabbiprimon00000@gmail.com or create an issue on GitHub.

