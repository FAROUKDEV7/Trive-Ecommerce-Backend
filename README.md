# TRIVÉ E-Commerce Backend

Production-ready Django REST API backend for the TRIVÉ fashion e-commerce platform.

## Tech Stack

- **Framework:** Django 4.2 + Django REST Framework 3.14
- **Database:** PostgreSQL
- **Auth:** JWT (SimpleJWT) + Google/Facebook OAuth
- **Payments:** Stripe
- **Task Queue:** Celery + Redis
- **Email:** SMTP (Gmail)

## Project Structure

```
trive_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── trive_backend/          # Main config
│   ├── settings.py
│   ├── urls.py
│   ├── pagination.py
│   ├── exceptions.py
│   ├── analytics.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── users/              # Auth, profiles, addresses
    ├── products/           # Products, categories, variants
    ├── cart/               # Shopping cart
    ├── wishlist/           # Wishlist
    ├── orders/             # Orders & tracking
    ├── coupons/            # Discount codes
    ├── reviews/            # Product reviews
    ├── payments/           # Stripe payments
    ├── notifications/      # User notifications
    └── contact/            # Contact form
```

## Setup

### 1. Clone and create virtual environment
```bash
git clone <repo>
cd trive_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 4. Setup PostgreSQL database
```bash
# Create database
createdb trive_db

# Or via psql:
psql -U postgres -c "CREATE DATABASE trive_db;"
psql -U postgres -c "CREATE USER trive_user WITH PASSWORD 'yourpassword';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE trive_db TO trive_user;"
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run development server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication (`/api/v1/auth/`)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/register/` | Register new user |
| POST | `/login/` | Login with email/password |
| POST | `/logout/` | Logout (blacklist token) |
| POST | `/token/refresh/` | Refresh JWT token |
| GET | `/verify-email/<token>/` | Verify email |
| POST | `/resend-verification/` | Resend verification email |
| POST | `/forgot-password/` | Request password reset |
| POST | `/reset-password/` | Reset password with token |
| POST | `/change-password/` | Change password (authenticated) |
| GET/PUT | `/profile/` | Get/update profile |
| GET/POST | `/addresses/` | List/create addresses |
| GET/PUT/DELETE | `/addresses/<id>/` | Address detail |
| POST | `/addresses/<id>/set-default/` | Set default address |

### Products (`/api/v1/products/`)
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/` | List products (filterable, searchable) | Public |
| GET | `/featured/` | Featured products | Public |
| GET | `/new-arrivals/` | New arrivals | Public |
| GET | `/sale/` | On-sale products | Public |
| GET | `/<slug>/` | Product detail | Public |
| GET | `/<slug>/related/` | Related products | Public |

#### Product Filters
- `?category=<slug>` - Filter by category
- `?min_price=100&max_price=500` - Price range
- `?is_featured=true` - Featured only
- `?is_on_sale=true` - On sale only
- `?in_stock=true` - In stock only
- `?size=M&color=Black` - By variant
- `?search=dress` - Full-text search
- `?ordering=price` or `?ordering=-price` - Sort

### Categories (`/api/v1/categories/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | All top-level categories (nested) |
| GET | `/<slug>/` | Category detail |

### Cart (`/api/v1/cart/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Get cart |
| POST | `/add/` | Add item to cart |
| PATCH | `/items/<id>/` | Update quantity |
| DELETE | `/items/<id>/remove/` | Remove item |
| DELETE | `/clear/` | Clear cart |

### Wishlist (`/api/v1/wishlist/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Get wishlist items |
| GET | `/ids/` | Get wishlist product IDs |
| POST | `/toggle/<product_id>/` | Toggle item in/out |

### Orders (`/api/v1/orders/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Order history |
| POST | `/create/` | Place order |
| GET | `/<id>/` | Order detail |
| POST | `/<id>/cancel/` | Cancel order |

### Coupons (`/api/v1/coupons/`)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/validate/` | Validate coupon code |

### Reviews (`/api/v1/reviews/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/products/<slug>/` | Product reviews |
| POST | `/create/` | Submit review |
| POST | `/<id>/helpful/` | Mark as helpful |

### Payments (`/api/v1/payments/`)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/create-intent/` | Create Stripe PaymentIntent |
| POST | `/webhook/` | Stripe webhook handler |

### Notifications (`/api/v1/notifications/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | All notifications + unread count |
| POST | `/mark-all-read/` | Mark all as read |
| PATCH | `/<id>/read/` | Mark one as read |

### Contact (`/api/v1/contact/`)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/` | Submit contact message |

### Admin Dashboard (`/api/v1/admin/`)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/dashboard/` | Revenue, orders, user stats |
| GET/POST | `/products/` (via products app) | Manage products |
| GET/PUT/DELETE | `/products/<id>/` | Product detail |
| GET | `/orders/all/` (via orders app) | All orders |
| POST | `/orders/<id>/status/` | Update order status |

## Social OAuth

Configure Google/Facebook apps and add credentials to `.env`.

The social auth redirect URLs are:
- Google: `/social-auth/complete/google-oauth2/`
- Facebook: `/social-auth/complete/facebook/`

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` or individual `DB_*` vars
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` - Gmail SMTP
- `GOOGLE_OAUTH2_CLIENT_ID` / `GOOGLE_OAUTH2_CLIENT_SECRET`
- `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY`

## Running in Production

```bash
# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn trive_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Start Celery worker
celery -A trive_backend worker --loglevel=info
```

## Admin Panel

Access at `/admin/` with superuser credentials.

Features:
- Manage all products, categories, orders, users
- Approve/reject reviews
- Create/manage discount coupons
- View contact messages"# Trive-Ecommerce-Backend" 
"# Trive-Ecommerce-Backend" 
"# Trive-Ecommerce-Backend" 
"# TRIV-E-Commerce-Backend" 
"# Trive-Ecommerce-Backend" 
