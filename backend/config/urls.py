"""
URL configuration for rental API project.

In Node.js/Express, this is similar to your main router file where you define:
app.use('/api/properties', propertyRoutes);

Django uses a different pattern but achieves the same result.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from backend.rentals.views import PropertyViewSet


@csrf_exempt
def api_root(request):
    """Root endpoint - health check and API info"""
    from django.conf import settings
    import os

    return JsonResponse({
        'status': 'online',
        'message': 'Rental Property API',
        'version': '1.0',
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'port': os.environ.get('PORT', 'not set'),
        'database_configured': bool(os.environ.get('DATABASE_URL')),
        'endpoints': {
            'properties': '/api/properties/',
            'admin': '/admin/',
            'api_docs': '/api/',
        }
    })

# Router automatically generates URL patterns for ViewSets
# Similar to Express Router but more automated
# In Node.js you'd manually define each route:
# router.get('/properties', getProperties)
# router.get('/properties/:id', getPropertyById)
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')

urlpatterns = [
    # Root endpoint - health check
    path('', api_root, name='api-root'),

    # Admin interface (Django's built-in admin panel)
    # Similar to tools like AdminJS in Node.js
    path('admin/', admin.site.urls),

    # API routes
    # /api/properties/ - List properties with filters
    # /api/properties/{id}/ - Get single property
    path('api/', include(router.urls)),

    # DRF's browsable API authentication
    path('api-auth/', include('rest_framework.urls')),
]
