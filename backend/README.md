# 🏠 Rental Properties API - Django Backend

RESTful API for property rental application with geolocation, filtering, and dynamic pricing capabilities built with Django, Django REST Framework, and PostGIS.

## 🎯 Features

- 🗺️ **PostGIS Geolocation** - Spatial queries with distance calculations
- 🔍 **Advanced Filtering** - Filter by type, price, location, amenities, dates, and more
- 📅 **Availability System** - Check property availability based on bookings
- 💰 **Dynamic Pricing** - Seasonal and date-based price calculations
- 🚀 **RESTful API** - Django REST Framework with ViewSets and Serializers
- 📊 **100 Sample Properties** - Pre-loaded database with realistic data
- 🔐 **CORS Enabled** - Ready for frontend integration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with PostGIS extension
- pip (Python package manager)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository:**
```bash
git clone <your-backend-repo-url>
cd rental-properties-backend
```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (Docker default values)
POSTGRES_DB=rental_db
POSTGRES_USER=rental_user
POSTGRES_PASSWORD=rental_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Run migrations:**
```bash
docker-compose exec web python manage.py migrate
```

5. **Import sample data:**
```bash
docker-compose exec web python manage.py import_data
```

6. **Create admin user (optional):**
```bash
docker-compose exec web python manage.py createsuperuser
```

7. **Access the API:**
```
http://localhost:8000/api/properties/
```

### Option 2: Local Setup (Without Docker)

1. **Clone and navigate:**
```bash
git clone <your-backend-repo-url>
cd rental-properties-backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL with PostGIS:**
```sql
-- In PostgreSQL (psql)
CREATE DATABASE rental_db;
CREATE USER rental_user WITH PASSWORD 'rental_password';
GRANT ALL PRIVILEGES ON DATABASE rental_db TO rental_user;

-- Connect to rental_db
\c rental_db
CREATE EXTENSION postgis;
```

5. **Create `.env` file:**
```bash
cp .env.example .env
```

Edit with your local PostgreSQL settings:
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=rental_db
POSTGRES_USER=rental_user
POSTGRES_PASSWORD=rental_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

6. **Run migrations:**
```bash
python manage.py migrate
```

7. **Import sample data:**
```bash
python manage.py import_data
```

8. **Start development server:**
```bash
python manage.py runserver
```

9. **Access the API:**
```
http://localhost:8000/api/properties/
```

## 📁 Project Structure

```
backend/
├── config/
│   ├── settings.py          # Django settings (DB, middleware, CORS)
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI application
├── rentals/
│   ├── models.py           # Database models (Property, Booking, etc.)
│   ├── views.py            # API ViewSets
│   ├── serializers.py      # DRF Serializers
│   ├── filters.py          # Filtering logic
│   └── management/
│       └── commands/
│           └── import_data.py  # Data import script
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── Procfile               # Production server command (Railway/Render)
├── railway.json           # Railway deployment config
├── runtime.txt            # Python version
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore patterns
└── docker-compose.yml    # Docker orchestration (optional)
```

## 🛠️ Tech Stack

- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Database:** PostgreSQL 15 with PostGIS 3.3
- **ORM:** Django ORM (GeoDjango for spatial queries)
- **Production Server:** Gunicorn
- **Static Files:** Whitenoise

### Node.js Equivalent Comparison

If you're coming from Node.js:
- **Django** ≈ Express.js (web framework)
- **Django REST Framework** ≈ Express + additional REST middleware
- **Django ORM** ≈ Sequelize, TypeORM, Prisma
- **psycopg2** ≈ 'pg' package (PostgreSQL driver)
- **python-decouple** ≈ 'dotenv'
- **django-cors-headers** ≈ 'cors' package
- **Gunicorn** ≈ PM2 or Node cluster mode

## 📡 API Endpoints

### Properties

```bash
# List properties with filters
GET /api/properties/
Query params: property_type, city, country, min_price, max_price,
              bedrooms, bathrooms, max_guests, amenities, check_in,
              check_out, latitude, longitude, radius, search, ordering

# Get single property
GET /api/properties/{id}/

# Nearby properties (geolocation)
GET /api/properties/nearby/?latitude=52.52&longitude=13.40&radius=10

# GeoJSON format (for mapping)
GET /api/properties/geojson/

# Property availability
GET /api/properties/{id}/availability/

# Dynamic price calculation
GET /api/properties/{id}/calculate_price/?check_in=2025-06-15&check_out=2025-06-20
```

### Example Requests

**Filter by city and price:**
```bash
curl "http://localhost:8000/api/properties/?city=Berlin&min_price=100&max_price=300"
```

**Geolocation search:**
```bash
curl "http://localhost:8000/api/properties/nearby/?latitude=52.5200&longitude=13.4050&radius=5"
```

**Check availability:**
```bash
curl "http://localhost:8000/api/properties/1/availability/"
```

**Calculate dynamic price:**
```bash
curl "http://localhost:8000/api/properties/1/calculate_price/?check_in=2025-07-01&check_out=2025-07-07"
```

## 🔍 Filter Options

### Basic Filters
- `property_type` - Apartment, House, Condo, Villa, etc.
- `city` - City name (case-insensitive partial match)
- `country` - Country name
- `min_price` / `max_price` - Price range per night
- `bedrooms` - Number of bedrooms (exact or minimum)
- `bathrooms` - Number of bathrooms
- `max_guests` - Maximum guest capacity

### Advanced Filters
- `amenities` - Comma-separated list (WiFi,Pool,Kitchen)
- `check_in` / `check_out` - Date range (YYYY-MM-DD)
- `latitude` / `longitude` / `radius` - Geolocation search (radius in km)
- `search` - Full-text search across name, description, city
- `ordering` - Sort by: `price`, `-price`, `bedrooms`, `distance`, etc.

### Pagination
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 20)

## 🗺️ PostGIS Geolocation

The API uses PostGIS for efficient spatial queries:

```python
# In models.py
location = gis_models.PointField(
    geography=True,  # Accurate distance calculations
    srid=4326,       # WGS84 coordinate system (GPS)
    db_index=True    # Spatial index (GIST)
)
```

**Distance Calculation:**
- Uses PostGIS `ST_DWithin` for radius queries
- Returns distance in kilometers
- Sorted by proximity to search point

**Spatial Indexes:**
- GIST index on `location` field for fast queries
- Composite indexes on commonly filtered fields

## 💰 Dynamic Pricing

Properties can have pricing rules that modify the base price:

```python
# Example: Summer pricing
{
    "season": "Summer",
    "start_date": "2025-06-01",
    "end_date": "2025-08-31",
    "price_multiplier": 1.30  # 30% increase
}
```

**Calculate Price Response:**
```json
{
    "property_id": 1,
    "property_name": "Cozy Apartment in Berlin",
    "check_in": "2025-07-01",
    "check_out": "2025-07-07",
    "nights": 6,
    "base_price_per_night": "150.00",
    "total_price": "1170.00",
    "average_price_per_night": "195.00",
    "daily_breakdown": [
        {
            "date": "2025-07-01",
            "base_price": "150.00",
            "multiplier": "1.30",
            "final_price": "195.00",
            "pricing_rule": "Summer Season"
        },
        // ... more days
    ]
}
```

## 🔐 Environment Variables

Create `.env` file with these variables:

### Development
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=rental_db
POSTGRES_USER=rental_user
POSTGRES_PASSWORD=rental_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Production (Railway/Render)
```bash
DJANGO_SECRET_KEY=strong-random-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app.up.railway.app

# DATABASE_URL is auto-provided by Railway/Render
DATABASE_URL=postgresql://user:pass@host:port/db

CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**Generate Secret Key:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 📊 Sample Data

The database includes:
- **100 properties** across 10 cities
- **10 property types** (Apartment, House, Villa, etc.)
- **13 amenity types** (WiFi, Pool, Kitchen, etc.)
- **266 bookings** (for availability testing)
- **188 pricing rules** (seasonal variations)
- **572 property images**

**Import Command:**
```bash
# Import all data
python manage.py import_data

# Clear existing data and import
python manage.py import_data --clear

# Import specific categories
python manage.py import_data --properties --amenities
```

## 🚀 Production Deployment

### Deploy to Railway (Recommended)

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Select your repository
   - Add PostgreSQL database
   - Railway auto-detects `railway.json` and `Procfile`

3. **Set Environment Variables:**
```bash
DJANGO_SECRET_KEY=<generate-new-one>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-app>.up.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

4. **Enable PostGIS:**
```bash
# Connect to Railway PostgreSQL
railway connect postgres

# In psql:
CREATE EXTENSION IF NOT EXISTS postgis;
```

5. **Run Migrations:**
```bash
railway run python manage.py migrate
railway run python manage.py import_data
```

**Complete deployment guide:** See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed instructions including Render deployment.

## 🐛 Troubleshooting

### PostGIS Extension Not Found
```
django.db.utils.OperationalError: type "geometry" does not exist
```
**Fix:**
```sql
-- In PostgreSQL
\c rental_db
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Module Import Errors
```
ModuleNotFoundError: No module named 'django'
```
**Fix:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### CORS Errors from Frontend
```
Access-Control-Allow-Origin error
```
**Fix:**
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`
- Ensure `corsheaders` is in `INSTALLED_APPS`
- Restart Django server

### Database Connection Error
```
could not connect to server: Connection refused
```
**Fix:**
- Check PostgreSQL is running: `pg_isready`
- Verify connection details in `.env`
- For Docker: `docker-compose ps` to check db service

## 🧪 Testing the API

### Using curl
```bash
# List all properties
curl http://localhost:8000/api/properties/

# Get property by ID
curl http://localhost:8000/api/properties/1/

# Filter by city
curl "http://localhost:8000/api/properties/?city=Berlin"

# Geolocation search
curl "http://localhost:8000/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5"

# Dynamic pricing
curl "http://localhost:8000/api/properties/1/calculate_price/?check_in=2025-06-15&check_out=2025-06-20"
```

### Using Django Admin
```bash
# Create superuser
python manage.py createsuperuser

# Access admin at: http://localhost:8000/admin/
```

### Using DRF Browsable API
Navigate to any endpoint in your browser for an interactive API interface:
```
http://localhost:8000/api/properties/
```

## 📚 Management Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Import sample data
python manage.py import_data

# Create admin user
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic

# Start development server
python manage.py runserver

# Open Django shell
python manage.py shell

# Show all URLs
python manage.py show_urls  # requires django-extensions
```

## 🔧 Development

### Adding New Endpoints
1. Create method in `rentals/views.py`:
```python
@action(detail=True, methods=['get'])
def my_custom_endpoint(self, request, pk=None):
    property_obj = self.get_object()
    # Your logic here
    return Response(data)
```

2. Access at: `/api/properties/{id}/my_custom_endpoint/`

### Adding New Filters
Edit `rentals/filters.py`:
```python
class PropertyFilter(django_filters.FilterSet):
    my_filter = django_filters.CharFilter(field_name='field')
```

### Modifying Models
1. Edit `rentals/models.py`
2. Run: `python manage.py makemigrations`
3. Run: `python manage.py migrate`

## 📖 Learn More

### Django Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [GeoDjango](https://docs.djangoproject.com/en/4.2/ref/contrib/gis/)
- [PostGIS](https://postgis.net/)

### Frontend Integration
This API is designed to work with a separate frontend application (Next.js, React, Vue, etc.).

**Frontend Repository:** [Link to your frontend repo]

**API Base URL:** `http://localhost:8000/api` (development) or `https://your-app.up.railway.app/api` (production)

## 🤝 Contributing

This is a standalone backend API that can be used with any frontend framework.

## 📝 License

MIT License - feel free to use this project for learning!

---

**Built with Django 4.2 + PostgreSQL + PostGIS**

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)
