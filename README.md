# 🏠 Rental Properties - Full Stack Application

Complete property rental system with Django backend and Next.js frontend, featuring geolocation search, dynamic pricing, and comprehensive filtering.

## 🎯 Overview

This project demonstrates a modern full-stack architecture with **separated frontend and backend** repositories that can be deployed independently.

```
┌─────────────────┐          ┌──────────────────┐
│   Next.js       │  HTTP    │   Django API     │
│   Frontend      │ ◄──────► │   Backend        │
│   (Vercel)      │  REST    │   (Railway)      │
└─────────────────┘          └──────────────────┘
                                      │
                              ┌───────▼────────┐
                              │  PostgreSQL    │
                              │  + PostGIS     │
                              └────────────────┘
```

## 📦 Repository Structure

This **monorepo** contains both applications for development purposes, but they should be deployed as **separate repositories** in production:

```
test-interview/                 (Current monorepo - for development only)
├── backend/                   → Split into rental-properties-backend repo
│   ├── config/
│   ├── rentals/
│   ├── requirements.txt
│   ├── Procfile
│   └── README.md
├── frontend/                  → Split into rental-properties-frontend repo
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   ├── vercel.json
│   └── README.md
├── sample-data.db            (Development data source)
├── docker-compose.yml        (Development environment)
└── README.md                 (This file)
```

## 🚀 Quick Start (Development)

### For Local Development (Both Apps Together)

Use this monorepo setup for local development:

```bash
# 1. Start both backend and frontend with Docker
docker-compose up

# 2. In a new terminal, run migrations
docker-compose exec web python manage.py migrate

# 3. Import sample data
docker-compose exec web python manage.py import_data

# Access the apps:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/api
# - Admin Panel: http://localhost:8000/admin
```

### For Production (Separate Deployments)

Each application has its own README with deployment instructions:

- **Backend:** See [backend/README.md](backend/README.md) - Deploy to Railway/Render
- **Frontend:** See [frontend/README.md](frontend/README.md) - Deploy to Vercel

## 📂 Splitting into Separate Repositories

When you're ready to deploy, split this monorepo into two separate repositories:

### 1. Create Backend Repository

```bash
# Create a new directory for backend repo
mkdir rental-properties-backend
cd rental-properties-backend

# Initialize git
git init

# Copy backend files
cp -r ../test-interview/backend/* .
cp ../test-interview/sample-data.db .

# Copy backend-specific files to root
mv requirements.txt ../
mv Procfile ../
mv runtime.txt ../
mv railway.json ../
mv .env.example ../

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
*.egg-info/

# Django
*.log
db.sqlite3
/staticfiles/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Database
*.db
*.sqlite
EOF

# Commit
git add .
git commit -m "Initial backend commit"

# Push to GitHub
git remote add origin <your-backend-repo-url>
git push -u origin main
```

### 2. Create Frontend Repository

```bash
# Create a new directory for frontend repo
mkdir rental-properties-frontend
cd rental-properties-frontend

# Initialize git
git init

# Copy frontend files
cp -r ../test-interview/frontend/* .

# Create .env.example
cat > .env.example << 'EOF'
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api
EOF

# Commit
git add .
git commit -m "Initial frontend commit"

# Push to GitHub
git remote add origin <your-frontend-repo-url>
git push -u origin main
```

### 3. Update Cross-References

After splitting:

**In backend README.md**, update:
```markdown
**Frontend Repository:** https://github.com/your-username/rental-properties-frontend
```

**In frontend README.md**, update:
```markdown
**Backend Repository:** https://github.com/your-username/rental-properties-backend
```

## 🎯 Key Features

### Backend (Django)
- ✅ RESTful API with Django REST Framework
- ✅ PostGIS geolocation with spatial indexes
- ✅ Dynamic pricing with seasonal variations
- ✅ Advanced filtering and search
- ✅ Property availability checking
- ✅ 100 sample properties with realistic data

### Frontend (Next.js)
- ✅ Interactive Leaflet map with markers
- ✅ Real-time property filtering
- ✅ Geolocation search (click-to-search)
- ✅ Dynamic pricing calculation
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Date range selection

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Database:** PostgreSQL 15 + PostGIS 3.3
- **Server:** Gunicorn (production)
- **Deployment:** Railway / Render

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Maps:** Leaflet + React Leaflet
- **HTTP Client:** Axios
- **Deployment:** Vercel

## 📚 Documentation

Each application has comprehensive documentation:

- **[Backend README](backend/README.md)** - API endpoints, setup, Django concepts
- **[Frontend README](frontend/README.md)** - Components, deployment, features
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide for both apps

## 🚀 Deployment Strategy

### Recommended Deployment

1. **Backend → Railway** (~$5/month)
   - Built-in PostgreSQL + PostGIS
   - Auto-deploys from Git
   - Easy environment variable management
   - Automatic SSL

2. **Frontend → Vercel** (Free)
   - Zero-config Next.js deployment
   - Edge network (CDN)
   - Auto-deploys from Git
   - Preview deployments for PRs

### Deployment Steps Summary

**Backend (Railway):**
```bash
1. Push backend code to separate GitHub repo
2. Create Railway project from GitHub
3. Add PostgreSQL database
4. Set environment variables
5. Enable PostGIS extension
6. Run migrations and import data
```

**Frontend (Vercel):**
```bash
1. Push frontend code to separate GitHub repo
2. Import project on Vercel
3. Set NEXT_PUBLIC_API_URL environment variable
4. Deploy (automatic)
5. Update backend CORS with Vercel URL
```

**Complete guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔗 Local Development Setup

### Option 1: Docker Compose (Recommended)

Run both apps together:

```bash
# Start all services
docker-compose up

# Run backend migrations
docker-compose exec web python manage.py migrate

# Import sample data
docker-compose exec web python manage.py import_data

# Create admin user (optional)
docker-compose exec web python manage.py createsuperuser
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/api
- Admin: http://localhost:8000/admin

### Option 2: Run Separately

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_data
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
npm run dev
```

## 🔍 API Examples

```bash
# List all properties
curl http://localhost:8000/api/properties/

# Filter by city and type
curl "http://localhost:8000/api/properties/?city=Berlin&property_type=Apartment"

# Geolocation search
curl "http://localhost:8000/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5"

# Dynamic pricing
curl "http://localhost:8000/api/properties/1/calculate_price/?check_in=2025-06-15&check_out=2025-06-20"
```

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check logs
docker-compose logs web

# Restart database
docker-compose restart db

# Re-import data
docker-compose exec web python manage.py import_data --clear
```

### Frontend Issues
```bash
# Check environment variable
cat frontend/.env.local

# Reinstall dependencies
cd frontend
rm -rf node_modules .next
npm install --legacy-peer-deps

# Check API connectivity
curl http://localhost:8000/api/properties/
```

### CORS Errors
- Ensure backend `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
- Restart backend after changing `.env`

## 📖 Learning Resources

### For Node.js Developers Learning Django
The backend code includes extensive comments comparing Django patterns to Node.js/Express equivalents.

**Topics covered:**
- Django vs Express routing
- Django ORM vs Sequelize/Prisma
- ViewSets vs Controllers
- Serializers vs DTOs
- Middleware comparison
- Environment variable handling

**See:** [backend/README.md](backend/README.md) for detailed comparisons

## 🎓 Project Structure Explained

### Monorepo (Development)
Use this for:
- Local development with Docker
- Running both apps together
- Quick prototyping
- Learning and experimentation

### Split Repos (Production)
Use this for:
- Independent deployments
- Separate version control
- Different team ownership
- Scalability (deploy frontend/backend to different platforms)

## 📝 Environment Variables

### Backend (.env)
```bash
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://...
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app/api
```

## 🤝 Contributing

This project demonstrates:
- Full-stack development with Django + Next.js
- Microservices architecture (separate frontend/backend)
- PostGIS geospatial queries
- RESTful API design
- Modern deployment practices

Feel free to use this as a template for your own projects!

## 📝 License

MIT License - free to use for learning and commercial projects.

---

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| Start both apps | `docker-compose up` |
| Run migrations | `docker-compose exec web python manage.py migrate` |
| Import data | `docker-compose exec web python manage.py import_data` |
| View backend logs | `docker-compose logs -f web` |
| View frontend logs | `docker-compose logs -f frontend` |
| Access PostgreSQL | `docker-compose exec db psql -U rental_user -d rental_db` |
| Stop all services | `docker-compose down` |

---

**Built with ❤️ using Django, PostgreSQL, PostGIS, Next.js, and TypeScript**

**Ready to deploy? See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions**
