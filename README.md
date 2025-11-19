# Rental Property API

Django REST API for rental property management with geolocation search, dynamic pricing, and comprehensive filtering capabilities.

## 🎯 Features

### Core Functionality
- **RESTful API** - Complete CRUD operations for properties, bookings, and pricing
- **Geolocation Search** - Find properties within radius using PostGIS spatial queries
- **Advanced Filtering** - Filter by city, country, property type, price range, bedrooms, bathrooms, and guests
- **Dynamic Pricing** - Seasonal pricing rules with custom multipliers per date range
- **Property Management** - Support for multiple property types (Apartment, House, Villa, Loft, etc.)
- **Booking System** - Track reservations with status management (confirmed, pending, cancelled)
- **Rich Property Data** - Images, amenities, and detailed property information

### Technical Features
- **PostGIS Integration** - Geographic queries with spatial indexes for fast location-based searches
- **Sample Data** - Pre-loaded with 50+ realistic properties across multiple cities
- **Admin Interface** - Django admin panel for easy data management
- **Browsable API** - Interactive API documentation via Django REST Framework
- **Production Ready** - Configured with Gunicorn, Whitenoise, and PostgreSQL

## 🛠️ Tech Stack

- **Django 4.2.7** - Python web framework
- **Django REST Framework 3.14.0** - RESTful API toolkit
- **PostgreSQL 15 + PostGIS 3.3** - Database with geospatial support
- **Gunicorn** - Production WSGI server
- **Whitenoise** - Static file serving
- **Python 3.11** - Programming language

## 🚀 Quick Start

### Option 1: Local Development with Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd test-interview

# Start PostgreSQL and Django
docker-compose up

# In another terminal, run migrations
docker-compose exec web python manage.py migrate

# Load sample data
docker-compose exec web python manage.py load_sample_data

# Create admin user (optional)
docker-compose exec web python manage.py createsuperuser
```

**Access the API:**
- API Root: http://localhost:8000/
- Properties List: http://localhost:8000/api/properties/
- Admin Panel: http://localhost:8000/admin/
- Browsable API: http://localhost:8000/api/

### Option 2: Local Development without Docker

```bash
# Install PostgreSQL with PostGIS extension
# macOS: brew install postgresql postgis
# Ubuntu: sudo apt-get install postgresql-15 postgresql-15-postgis-3

# Create database
createdb rental_db
psql rental_db -c "CREATE EXTENSION postgis;"

# Setup Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
cd backend
python manage.py migrate

# Load sample data
python manage.py load_sample_data

# Run development server
python manage.py runserver
```

## 📡 API Endpoints

### Properties

```bash
# List all properties with pagination
GET /api/properties/

# Filter properties
GET /api/properties/?city=Berlin&property_type=Apartment&bedrooms=2&max_price=500

# Get single property with details
GET /api/properties/{id}/

# Geolocation search (find properties within radius)
GET /api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5

# Calculate price for date range
GET /api/properties/{id}/calculate_price/?check_in=2025-06-15&check_out=2025-06-20
```

### Health Check

```bash
# API status and configuration
GET /
```

### Admin

```bash
# Django admin panel
GET /admin/
```

## 📊 API Response Examples

### List Properties
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/properties/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Loft in Berlin",
      "description": "Beautiful loft in central Berlin...",
      "property_type": "Loft",
      "address": "32057 Hill Haven",
      "city": "Berlin",
      "country": "Germany",
      "latitude": 52.578296,
      "longitude": 13.474558,
      "bedrooms": 1,
      "bathrooms": 1.5,
      "max_guests": 2,
      "base_price_per_night": 409.72,
      "currency": "USD",
      "images": [...],
      "amenities": [...],
      "created_at": "2025-11-10T17:01:11Z"
    }
  ]
}
```

### Filter Examples
```bash
# Properties in Berlin
curl "http://localhost:8000/api/properties/?city=Berlin"

# Apartments with 2+ bedrooms under $300/night
curl "http://localhost:8000/api/properties/?property_type=Apartment&bedrooms=2&max_price=300"

# Properties for 4 guests
curl "http://localhost:8000/api/properties/?min_guests=4"

# Nearby search (5km radius)
curl "http://localhost:8000/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5"
```

## 🏗️ Project Structure

```
test-interview/
├── backend/
│   ├── config/              # Django configuration
│   │   ├── settings.py      # App settings
│   │   ├── urls.py          # URL routing
│   │   └── wsgi.py          # WSGI config
│   ├── rentals/             # Main application
│   │   ├── models.py        # Data models (Property, Booking, etc.)
│   │   ├── views.py         # API views
│   │   ├── serializers.py   # Data serialization
│   │   ├── filters.py       # Query filters
│   │   └── management/
│   │       └── commands/
│   │           └── load_sample_data.py  # Data loader
│   └── manage.py            # Django CLI
├── sample-data.db           # SQLite sample data
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Local development setup
├── start.sh               # Production startup script
└── README.md              # This file
```

## 🚢 Railway Deployment

Complete deployment guide: [RAILWAY_SETUP.md](RAILWAY_SETUP.md)

**Quick Deploy:**

1. Push to GitHub
2. Create Railway project from repo
3. Add PostgreSQL database
4. Set environment variables:
   ```bash
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<generate-secret-key>
   DJANGO_ALLOWED_HOSTS=.railway.app
   ```
5. Deploy automatically handles:
   - Database migrations
   - Sample data loading
   - Static file collection
   - PostGIS setup

**Live Demo:** https://rental-property-backend-production.up.railway.app/

## 🔧 Available Management Commands

```bash
# Load sample data into database
python manage.py load_sample_data

# Create superuser for admin panel
python manage.py createsuperuser

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

## 🧪 Testing the API

```bash
# Health check
curl http://localhost:8000/

# List properties
curl http://localhost:8000/api/properties/

# Get property details
curl http://localhost:8000/api/properties/1/

# Search by location
curl "http://localhost:8000/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=10"

# Filter and search
curl "http://localhost:8000/api/properties/?city=Berlin&bedrooms=2&max_price=400"
```

## 📝 Environment Variables

```bash
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True  # False in production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development)
POSTGRES_DB=rental_db
POSTGRES_USER=rental_user
POSTGRES_PASSWORD=rental_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Database (Production - Railway auto-provides this)
DATABASE_URL=postgresql://...

# CORS (if frontend is on different domain)
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

## 🎓 For Node.js Developers

This project includes extensive code comments comparing Django patterns to Node.js/Express equivalents:

- **Models** → Sequelize/Prisma/TypeORM models
- **Views** → Express controllers
- **Serializers** → DTOs/validation schemas
- **URLs** → Express routing
- **Middleware** → Express middleware

See inline comments in the code for detailed comparisons.

## 📄 License

MIT License - Free to use for learning and commercial projects
