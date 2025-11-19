# Complete Setup Guide - Rental Properties Application

Full-stack rental properties application with Django + PostGIS backend and Next.js 14 frontend.

## 🎯 What You Have

### Backend (Django + PostGIS)
- ✅ PostgreSQL database with PostGIS extension
- ✅ Django REST API with geolocation support
- ✅ 100 properties imported from SQLite
- ✅ Advanced filtering (type, price, location, dates, amenities)
- ✅ Geolocation queries with spatial indexes
- ✅ Hot reload for development

### Frontend (Next.js 14)
- ✅ Interactive Leaflet map
- ✅ Property cards and listings
- ✅ Comprehensive filter sidebar
- ✅ Geolocation search (click on map)
- ✅ TypeScript + Tailwind CSS
- ✅ Hot reload for development

## 🚀 Complete Setup (3 Commands)

### 1. Start All Services

```bash
docker-compose up --build
```

This starts:
- PostgreSQL with PostGIS (port 5432)
- Django API (port 8000)
- Next.js Frontend (port 3000)

### 2. Run Database Migrations

```bash
docker-compose exec web python manage.py makemigrations rentals
docker-compose exec web python manage.py migrate
```

### 3. Import Data

```bash
docker-compose exec web python manage.py import_data --clear
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/properties/
- **Admin Panel**: http://localhost:8000/admin/

## 📋 Testing the Application

### 1. Frontend Testing

Open http://localhost:3000

**Test Filters:**
- Select "Apartment" in Property Type
- Enter "Berlin" in City
- Set Price range: Min 100, Max 500
- Set Min Bedrooms: 2
- Select amenities: WiFi, Pool
- Click "Show Map"
- Click on the map to search nearby properties

### 2. Backend API Testing

```bash
# List all properties
curl http://localhost:8000/api/properties/

# Filter by city
curl "http://localhost:8000/api/properties/?city=Berlin"

# Price range
curl "http://localhost:8000/api/properties/?min_price=100&max_price=500"

# Bedrooms
curl "http://localhost:8000/api/properties/?bedrooms__gte=2"

# Multiple filters
curl "http://localhost:8000/api/properties/?city=Berlin&bedrooms__gte=2&max_price=500&amenities=WiFi,Pool"

# Geolocation (within 5km of Berlin center)
curl "http://localhost:8000/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5"

# Get property details
curl http://localhost:8000/api/properties/1/

# Check availability
curl http://localhost:8000/api/properties/1/availability/
```

## 📂 Project Structure

```
test-interview/
├── backend/                    # Django application
│   ├── config/                # Django settings
│   │   ├── settings.py       # Database, CORS, REST framework config
│   │   ├── urls.py           # API routes
│   │   └── wsgi.py           # WSGI config
│   └── rentals/              # Main app
│       ├── models.py         # Property, Booking, Amenity models
│       ├── serializers.py    # JSON serialization
│       ├── views.py          # API endpoints
│       ├── filters.py        # Filter logic
│       ├── admin.py          # Admin interface
│       └── management/
│           └── commands/
│               └── import_data.py  # Data import script
├── frontend/                  # Next.js application
│   ├── app/
│   │   └── page.tsx          # Main page with filters & map
│   ├── components/
│   │   ├── PropertyCard.tsx  # Property card
│   │   ├── PropertyFilters.tsx  # Filter sidebar
│   │   └── PropertyMap.tsx   # Leaflet map
│   └── lib/
│       ├── api.ts            # API client
│       └── types.ts          # TypeScript types
├── docker-compose.yml         # All services configuration
├── Dockerfile                 # Django container
├── frontend/Dockerfile        # Next.js container
├── sample-data.db            # Source SQLite database
└── README.md                 # Main documentation
```

## 🔧 Development Workflow

### Making Changes to Backend

1. Edit files in `backend/`
2. Django automatically reloads
3. No need to restart container

Example:
```bash
# Edit backend/rentals/views.py
# Changes apply immediately
```

### Making Changes to Frontend

1. Edit files in `frontend/`
2. Next.js automatically reloads
3. Browser refreshes automatically

Example:
```bash
# Edit frontend/app/page.tsx
# Browser refreshes automatically
```

### Adding New Django Migrations

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 🗺️ How Geolocation Works

### Backend (PostGIS)

1. **PointField** stores coordinates as geometry
2. **Spatial indexes** (GIST) enable fast queries
3. **Distance calculations** use Earth's curvature
4. **Filters** use `ST_DWithin` and `ST_Distance`

```python
# In models.py
location = gis_models.PointField(geography=True, srid=4326)

# In views.py
properties = Property.objects.filter(
    location__dwithin=(user_location, D(km=radius))
).annotate(
    distance=Distance('location', user_location)
).order_by('distance')
```

### Frontend (Leaflet)

1. **User clicks map** → gets lat/lng coordinates
2. **Circle appears** showing search radius
3. **API called** with latitude, longitude, radius
4. **Results filtered** by distance
5. **Map updates** with nearby properties

```tsx
// In PropertyMap.tsx
const handleMapClick = (e) => {
  const { lat, lng } = e.latlng;
  onLocationSelect(lat, lng, radius);
  // Triggers API: /api/properties/?latitude=X&longitude=Y&radius=Z
};
```

## 📊 Database Schema

### Properties Table

```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    property_type VARCHAR(50),
    city VARCHAR(100),
    country VARCHAR(100),
    location GEOMETRY(Point, 4326),  -- PostGIS!
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    max_guests INTEGER,
    base_price_per_night DECIMAL(10,2),
    -- ... indexes on location, city, price, etc.
);
```

### Indexes for Performance

- Spatial index on `location` (GIST)
- B-tree indexes on `city`, `property_type`, `base_price_per_night`
- Composite indexes on frequently combined filters

## 🎨 Frontend Components

### Main Page Flow

```
User visits http://localhost:3000
    ↓
page.tsx loads
    ↓
Fetches properties from API
    ↓
Displays PropertyCards in grid
    ↓
User clicks "Show Map"
    ↓
PropertyMap component loads
    ↓
User applies filters
    ↓
PropertyFilters updates state
    ↓
useEffect triggers new API call
    ↓
Results update in real-time
```

### Filter System

```
PropertyFilters Component
    ↓
User changes filter
    ↓
handleFilterChange(newFilters)
    ↓
Parent component updates state
    ↓
useEffect detects change
    ↓
fetchProperties(filters) called
    ↓
API returns filtered results
    ↓
UI updates
```

## 🐛 Troubleshooting

### Frontend Can't Connect to API

**Problem**: `Network Error` or `CORS error`

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/api/properties/

# Check Django CORS settings
# backend/config/settings.py should have:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Map Not Showing

**Problem**: Blank map area

**Solution**:
1. Check browser console for errors
2. Verify Leaflet CSS is imported in `globals.css`
3. Ensure component has `'use client'` directive

### Database Connection Error

**Problem**: Django can't connect to PostgreSQL

**Solution**:
```bash
# Check if database container is running
docker-compose ps

# Restart database
docker-compose restart db

# Wait for database to be ready
docker-compose logs db
```

### No Properties Showing

**Problem**: Empty list

**Solution**:
```bash
# Check if data was imported
docker-compose exec db psql -U rental_user -d rental_db -c "SELECT COUNT(*) FROM properties;"

# Re-import if needed
docker-compose exec web python manage.py import_data --clear
```

## 🚀 Next Steps

### Add More Features

1. **Property Details Page**
   - Create `frontend/app/properties/[id]/page.tsx`
   - Show full description, all images, calendar
   - Display unavailable dates

2. **Pagination**
   - Use `next`/`previous` URLs from API
   - Add page navigation component

3. **Favorites**
   - Add local storage for saved properties
   - Create favorites page

4. **Advanced Map Features**
   - Clustering for many markers
   - Heat maps for price ranges
   - Draw tools for custom areas

### Production Deployment

1. **Backend**:
   - Use Gunicorn instead of Django dev server
   - Set `DEBUG=False`
   - Use managed PostgreSQL (AWS RDS, etc.)
   - Add Nginx for static files

2. **Frontend**:
   - Run `npm run build`
   - Use production Next.js server
   - Deploy to Vercel or similar

3. **Environment**:
   - Separate `.env` files for production
   - Use secrets management
   - Configure HTTPS

## 📚 Documentation

- **Backend**: See [README.md](README.md)
- **Frontend**: See [FRONTEND_README.md](FRONTEND_README.md)
- **Quick Setup**: See [SETUP.md](SETUP.md)

## 🎓 Learning Resources

### Django + PostGIS
- [GeoDjango Tutorial](https://docs.djangoproject.com/en/4.2/ref/contrib/gis/tutorial/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [Django REST Framework](https://www.django-rest-framework.org/)

### Next.js + Leaflet
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [React Leaflet](https://react-leaflet.js.org/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## ✅ Verification Checklist

- [ ] All Docker containers running (`docker-compose ps`)
- [ ] Database migrations applied
- [ ] 100 properties imported
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API accessible at http://localhost:8000/api/properties/
- [ ] Map shows property markers
- [ ] Filters work correctly
- [ ] Geolocation search works (click on map)
- [ ] Property cards display correctly

## 🎉 Success!

You now have a complete full-stack rental properties application with:
- Django backend with geospatial queries
- Next.js frontend with interactive maps
- Complete filtering system
- Real-time updates
- Hot reload for development

**Start exploring at http://localhost:3000!**
