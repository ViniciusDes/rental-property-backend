# Quick Setup Guide

## Steps to Get Your API Running

### 1. Restart the Container (You're doing this now)
```bash
docker-compose restart web
# or
docker-compose down && docker-compose up -d
```

### 2. Run Database Migrations
This creates all the database tables from the Django models:
```bash
docker-compose exec web python manage.py migrate
```

**In Node.js equivalent:** `npx sequelize-cli db:migrate`

### 3. Import Data from SQLite
This imports all 100 properties and related data:
```bash
docker-compose exec web python manage.py import_data --clear
```

**In Node.js equivalent:** `node scripts/import-data.js`

### 4. Create Admin User (Optional)
To access Django's admin panel at http://localhost:8000/admin/:
```bash
docker-compose exec web python manage.py createsuperuser
```

Enter username, email, and password when prompted.

### 5. Test the API
```bash
# List all properties
curl http://localhost:8000/api/properties/

# Get property #1 details
curl http://localhost:8000/api/properties/1/

# Filter by city
curl "http://localhost:8000/api/properties/?city=Berlin"

# Geolocation search (5km radius from Berlin center)
curl "http://localhost:8000/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5"
```

### 6. View in Browser
- **API Root**: http://localhost:8000/api/
- **Properties List**: http://localhost:8000/api/properties/
- **Admin Panel**: http://localhost:8000/admin/ (if you created superuser)

Django REST Framework provides a nice browsable web interface!

## Common Commands

```bash
# View logs
docker-compose logs -f web

# Access Django shell (like Node.js REPL)
docker-compose exec web python manage.py shell

# Access database
docker-compose exec db psql -U rental_user -d rental_db

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

## Troubleshooting

### Container won't start?
```bash
docker-compose down -v
docker-compose up --build
```

### Database connection error?
Wait a few seconds for PostgreSQL to fully start, then:
```bash
docker-compose restart web
```

### Import fails?
Make sure migrations ran first:
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py import_data --clear
```
