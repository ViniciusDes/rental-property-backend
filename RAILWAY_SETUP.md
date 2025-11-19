# Railway Deployment - Complete Setup Guide

## 🚀 Quick Deploy Checklist

### 1. Required Environment Variables in Railway

Go to Railway Dashboard → Your Service → Variables and set:

```bash
# Required
DATABASE_URL=<auto-set-by-railway-postgres>
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=z&nc37fpu*76*u_yqwunf7fdz(f_e4^^6_o)@ep*!a\!s@f5ex
DJANGO_ALLOWED_HOSTS=rental-property-backend-production.up.railway.app,.railway.app

# Optional (only if you have a specific frontend)
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### 2. Add PostgreSQL Database

1. In Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. DATABASE_URL is automatically set

### 3. Deploy

```bash
git add .
git commit -m "Add Railway deployment with startup script"
git push
```

## 📝 What's Automated

✅ Database migrations (`python manage.py migrate`)
✅ Sample data loading (`python manage.py load_sample_data`)
✅ Static file collection (`python manage.py collectstatic`)
✅ Gunicorn server with 4 workers
✅ Detailed logging for debugging
✅ Fault-tolerant startup (continues even if sample data exists)

## 🔍 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://rental-property-backend-production.up.railway.app/

# List properties
curl https://rental-property-backend-production.up.railway.app/api/properties/

# Get specific property
curl https://rental-property-backend-production.up.railway.app/api/properties/1/

# Django admin
# https://rental-property-backend-production.up.railway.app/admin/
```

## 🐛 Troubleshooting 502 Errors

### Check Railway Logs

1. Go to Railway Dashboard → Your Service → Deployments
2. Click on the latest deployment
3. Check the logs for errors

### Common Issues:

**1. Missing DATABASE_URL**
- Make sure PostgreSQL service is added
- Verify DATABASE_URL variable exists

**2. Wrong ALLOWED_HOSTS**
- Set: `DJANGO_ALLOWED_HOSTS=rental-property-backend-production.up.railway.app,.railway.app`
- The `.railway.app` allows all Railway subdomains

**3. DEBUG=True in production**
- Must set: `DJANGO_DEBUG=False`

**4. Startup command failing**
- Check logs for which step fails (migrate, load_sample_data, collectstatic)
- The new start.sh script provides detailed logging

## 📊 Expected Logs

Successful deployment should show:

```
=== Starting Django Application ===
Step 1: Running database migrations...
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, rentals, sessions
Running migrations:
  No migrations to apply.

Step 2: Loading sample data...
Loading sample data from sample-data.db...
Loaded 50 properties
Loaded 150 property images
Loaded 200 property amenities
Loaded 75 pricing rules
Loaded 30 bookings
Successfully loaded all sample data!

Step 3: Collecting static files...
168 static files copied to '/app/staticfiles', 486 post-processed.

Step 4: Starting Gunicorn...
Port: 8080
Workers: 4
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: sync
[INFO] Booting worker with pid: 12
[INFO] Booting worker with pid: 13
[INFO] Booting worker with pid: 14
[INFO] Booting worker with pid: 15
```

## 🔐 Create Superuser

After deployment, create an admin account:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link
railway login
railway link

# Create superuser
railway run python manage.py createsuperuser
```

Then access: https://rental-property-backend-production.up.railway.app/admin/

## 📁 Key Files

- **Dockerfile** - Container build configuration
- **start.sh** - Startup script with logging
- **railway.json** - Railway deployment config
- **requirements.txt** - Python dependencies
- **backend/config/settings.py** - Django settings
- **backend/rentals/management/commands/load_sample_data.py** - Data loader

## 🎯 Next Steps

1. ✅ Set environment variables in Railway
2. ✅ Add PostgreSQL database
3. ✅ Deploy (git push)
4. ✅ Verify endpoints work
5. ✅ Create superuser
6. ✅ Test Django admin

## 🔗 Your Endpoints

- **API Root**: https://rental-property-backend-production.up.railway.app/
- **Properties List**: https://rental-property-backend-production.up.railway.app/api/properties/
- **Single Property**: https://rental-property-backend-production.up.railway.app/api/properties/1/
- **Admin Panel**: https://rental-property-backend-production.up.railway.app/admin/
- **Browsable API**: https://rental-property-backend-production.up.railway.app/api/

## ✅ Deployment Complete!

Your Django API is now fully configured for Railway with:
- ✅ Automated database setup
- ✅ Sample data loading
- ✅ Production-ready Gunicorn server
- ✅ PostGIS geolocation support
- ✅ Static file serving
- ✅ Comprehensive logging
