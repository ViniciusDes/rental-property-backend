"""
Django REST Framework Views (ViewSets)

COMPARISON WITH NODE.JS:
========================

In Node.js/Express, you'd create route handlers:
```javascript
// Controller functions
const getProperties = async (req, res) => {
  const properties = await Property.findAll({ where: {...} });
  res.json(properties);
};

const getPropertyById = async (req, res) => {
  const property = await Property.findByPk(req.params.id);
  res.json(property);
};

// Routes
router.get('/properties', getProperties);
router.get('/properties/:id', getPropertyById);
```

Django ViewSets combine all CRUD operations in one class and
automatically generate routes. We only need LIST and RETRIEVE (GET operations).
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Property
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyGeoJSONSerializer
)
from .filters import PropertyFilter


class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Property API

    ReadOnlyModelViewSet provides:
    - list() -> GET /api/properties/
    - retrieve() -> GET /api/properties/{id}/

    In Node.js, this is equivalent to:
    ```javascript
    class PropertyController {
      async list(req, res) { ... }
      async getById(req, res) { ... }
    }
    ```

    AVAILABLE ENDPOINTS:
    ===================

    1. List Properties:
       GET /api/properties/

       Query Parameters:
       - property_type: Apartment, House, Condo, etc.
       - min_price: Minimum price per night
       - max_price: Maximum price per night
       - bedrooms: Exact number of bedrooms
       - bedrooms__gte: Minimum number of bedrooms
       - bathrooms: Exact number of bathrooms
       - bathrooms__gte: Minimum number of bathrooms
       - city: City name (partial match)
       - country: Country name (partial match)
       - amenities: Comma-separated list (e.g., WiFi,Pool,Kitchen)
       - check_in: Check-in date (YYYY-MM-DD)
       - check_out: Check-out date (YYYY-MM-DD)
       - latitude: Latitude for proximity search
       - longitude: Longitude for proximity search
       - radius: Radius in kilometers (default: 10km)
       - ordering: Sort by field (e.g., -base_price_per_night, bedrooms)
       - search: Search in name, description, city
       - page: Page number (default: 1)
       - page_size: Items per page (default: 20)

    2. Get Property Details:
       GET /api/properties/{id}/

    3. Get Properties as GeoJSON:
       GET /api/properties/geojson/

    4. Search Nearby Properties:
       GET /api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5
    """

    queryset = Property.objects.prefetch_related(
        'amenities',
        'images',
        'bookings'
    ).all()

    # In Node.js, prefetch_related is like eager loading:
    # Property.findAll({ include: [PropertyAmenity, PropertyImage, Booking] })

    # Filter backends
    # Similar to middleware in Express that processes query parameters
    filter_backends = [
        DjangoFilterBackend,  # Handles complex filtering
        OrderingFilter,       # Handles sorting
        SearchFilter,         # Handles text search
    ]

    # Filter configuration
    filterset_class = PropertyFilter

    # Ordering configuration
    # Usage: ?ordering=-base_price_per_night (descending)
    # In Node.js: ORDER BY base_price_per_night DESC
    ordering_fields = [
        'base_price_per_night',
        'bedrooms',
        'bathrooms',
        'created_at',
        'name'
    ]
    ordering = ['-created_at']  # Default ordering

    # Search configuration
    # Usage: ?search=berlin apartment
    # In Node.js: WHERE name LIKE '%berlin%' OR description LIKE '%berlin%'
    search_fields = ['name', 'description', 'city', 'address']

    def get_serializer_class(self):
        """
        Return different serializers for list vs detail views

        In Node.js:
        ```javascript
        const getSerializer = (action) => {
          if (action === 'list') return PropertyListDTO;
          if (action === 'detail') return PropertyDetailDTO;
        };
        ```
        """
        if self.action == 'list':
            return PropertyListSerializer
        elif self.action == 'retrieve':
            return PropertyDetailSerializer
        elif self.action == 'geojson':
            return PropertyGeoJSONSerializer
        return PropertyDetailSerializer

    def get_queryset(self):
        """
        Customize the queryset based on query parameters

        In Node.js:
        ```javascript
        let query = Property.findAll();

        if (req.query.latitude && req.query.longitude) {
          // Add distance calculation
          query = Property.findAll({
            attributes: {
              include: [
                [sequelize.fn('ST_Distance', ...), 'distance']
              ]
            }
          });
        }
        ```
        """
        queryset = super().get_queryset()

        # Geolocation filtering using PostGIS
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        radius = self.request.query_params.get('radius', 10)  # Default 10km

        if latitude and longitude:
            try:
                # Create a Point from the provided coordinates
                user_location = Point(
                    float(longitude),
                    float(latitude),
                    srid=4326  # WGS84 coordinate system
                )

                # Filter properties within the radius
                # This uses PostGIS ST_DWithin for efficient spatial queries
                # In Node.js with PostGIS:
                # ```sql
                # SELECT *, ST_Distance(location, ST_Point(lng, lat)) as distance
                # FROM properties
                # WHERE ST_DWithin(location, ST_Point(lng, lat), radius_in_meters)
                # ORDER BY distance
                # ```
                queryset = queryset.filter(
                    location__dwithin=(user_location, D(km=float(radius)))
                ).annotate(
                    distance=Distance('location', user_location)
                ).order_by('distance')

            except (ValueError, TypeError):
                # Invalid latitude/longitude values
                pass

        return queryset

    def list(self, request, *args, **kwargs):
        """
        List properties with filters

        In Node.js/Express:
        ```javascript
        router.get('/properties', async (req, res) => {
          const properties = await Property.findAll({
            where: buildWhereClause(req.query),
            limit: req.query.page_size || 20,
            offset: (req.query.page - 1) * page_size
          });

          res.json({
            count: total,
            next: nextPageUrl,
            previous: prevPageUrl,
            results: properties
          });
        });
        ```
        """
        # Call the parent list method (handles pagination automatically)
        response = super().list(request, *args, **kwargs)

        # Add custom metadata to response
        response.data['filters_applied'] = {
            'property_type': request.query_params.get('property_type'),
            'city': request.query_params.get('city'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'geolocation': bool(
                request.query_params.get('latitude') and
                request.query_params.get('longitude')
            )
        }

        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single property with all details

        In Node.js/Express:
        ```javascript
        router.get('/properties/:id', async (req, res) => {
          const property = await Property.findByPk(req.params.id, {
            include: [PropertyAmenity, PropertyImage, Booking]
          });

          if (!property) {
            return res.status(404).json({ error: 'Property not found' });
          }

          res.json(property);
        });
        ```
        """
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """
        Return properties in GeoJSON format for map visualization

        Custom endpoint: GET /api/properties/geojson/

        In Node.js:
        ```javascript
        router.get('/properties/geojson', async (req, res) => {
          const properties = await Property.findAll();

          const geoJSON = {
            type: 'FeatureCollection',
            features: properties.map(p => ({
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: [p.longitude, p.latitude]
              },
              properties: {
                id: p.id,
                name: p.name,
                price: p.base_price_per_night
              }
            }))
          };

          res.json(geoJSON);
        });
        ```

        Django GeoFeatureModelSerializer handles this automatically!
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = PropertyGeoJSONSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Find properties near a specific location

        Custom endpoint: GET /api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5

        In Node.js with PostGIS:
        ```javascript
        router.get('/properties/nearby', async (req, res) => {
          const { latitude, longitude, radius = 10 } = req.query;

          const properties = await sequelize.query(`
            SELECT *,
              ST_Distance(
                location,
                ST_SetSRID(ST_Point(:longitude, :latitude), 4326)
              ) / 1000 as distance_km
            FROM properties
            WHERE ST_DWithin(
              location,
              ST_SetSRID(ST_Point(:longitude, :latitude), 4326),
              :radius * 1000
            )
            ORDER BY distance_km
          `, {
            replacements: { latitude, longitude, radius },
            type: QueryTypes.SELECT
          });

          res.json(properties);
        });
        ```
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius', 10)

        if not latitude or not longitude:
            return Response(
                {
                    'error': 'latitude and longitude are required',
                    'example': '/api/properties/nearby/?latitude=52.52&longitude=13.40&radius=5'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_location = Point(float(longitude), float(latitude), srid=4326)

            # Find properties within radius
            properties = Property.objects.filter(
                location__dwithin=(user_location, D(km=float(radius)))
            ).annotate(
                distance=Distance('location', user_location)
            ).order_by('distance')

            serializer = PropertyListSerializer(properties, many=True)

            return Response({
                'count': properties.count(),
                'radius_km': float(radius),
                'center': {
                    'latitude': float(latitude),
                    'longitude': float(longitude)
                },
                'results': serializer.data
            })

        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid parameters: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Get availability calendar for a specific property

        Custom endpoint: GET /api/properties/{id}/availability/?month=2025-12

        In Node.js:
        ```javascript
        router.get('/properties/:id/availability', async (req, res) => {
          const property = await Property.findByPk(req.params.id);
          const bookings = await Booking.findAll({
            where: {
              property_id: property.id,
              status: 'confirmed'
            }
          });

          const unavailableDates = bookings.map(b => ({
            check_in: b.check_in,
            check_out: b.check_out
          }));

          res.json({ unavailableDates });
        });
        ```
        """
        property_obj = self.get_object()

        confirmed_bookings = property_obj.bookings.filter(
            status='confirmed'
        ).order_by('check_in')

        unavailable_dates = [
            {
                'check_in': booking.check_in.isoformat(),
                'check_out': booking.check_out.isoformat()
            }
            for booking in confirmed_bookings
        ]

        return Response({
            'property_id': property_obj.id,
            'property_name': property_obj.name,
            'unavailable_dates': unavailable_dates,
            'total_bookings': len(unavailable_dates)
        })

    @action(detail=True, methods=['get'])
    def calculate_price(self, request, pk=None):
        """
        Calculate total price for a date range with dynamic pricing

        Custom endpoint: GET /api/properties/{id}/calculate_price/?check_in=2025-12-01&check_out=2025-12-07

        This implements DYNAMIC PRICING by:
        1. Getting the base price per night
        2. Applying seasonal/date-based pricing rules
        3. Calculating total for the entire stay

        In Node.js:
        ```javascript
        router.get('/properties/:id/calculate-price', async (req, res) => {
          const { check_in, check_out } = req.query;
          const property = await Property.findByPk(req.params.id);

          let totalPrice = 0;
          let currentDate = new Date(check_in);
          const endDate = new Date(check_out);

          while (currentDate < endDate) {
            // Check for pricing rules for this date
            const rule = await PricingRule.findOne({
              where: {
                property_id: property.id,
                start_date: { [Op.lte]: currentDate },
                end_date: { [Op.gte]: currentDate }
              }
            });

            const multiplier = rule ? rule.price_multiplier : 1.0;
            totalPrice += property.base_price_per_night * multiplier;
            currentDate.setDate(currentDate.getDate() + 1);
          }

          res.json({ total_price: totalPrice, nights: nights });
        });
        ```
        """
        from datetime import datetime, timedelta
        from decimal import Decimal

        property_obj = self.get_object()

        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')

        if not check_in_str or not check_out_str:
            return Response(
                {
                    'error': 'check_in and check_out dates are required',
                    'example': '/api/properties/1/calculate_price/?check_in=2025-12-01&check_out=2025-12-07'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

            if check_out <= check_in:
                return Response(
                    {'error': 'check_out must be after check_in'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate number of nights
            nights = (check_out - check_in).days

            # Get all pricing rules for this property
            pricing_rules = property_obj.pricing_rules.all()

            # Calculate total price day by day
            total_price = Decimal('0.00')
            daily_prices = []
            current_date = check_in

            while current_date < check_out:
                # Find applicable pricing rule for this date
                multiplier = Decimal('1.0')
                rule_name = 'Base Rate'

                for rule in pricing_rules:
                    if rule.start_date <= current_date <= rule.end_date:
                        multiplier = rule.price_multiplier
                        rule_name = f'Seasonal ({rule.start_date} to {rule.end_date})'
                        break

                # Calculate price for this night
                night_price = property_obj.base_price_per_night * multiplier
                total_price += night_price

                daily_prices.append({
                    'date': current_date.isoformat(),
                    'base_price': str(property_obj.base_price_per_night),
                    'multiplier': str(multiplier),
                    'final_price': str(night_price),
                    'pricing_rule': rule_name
                })

                current_date += timedelta(days=1)

            # Calculate average price per night
            avg_price_per_night = total_price / nights if nights > 0 else Decimal('0.00')

            return Response({
                'property_id': property_obj.id,
                'property_name': property_obj.name,
                'check_in': check_in.isoformat(),
                'check_out': check_out.isoformat(),
                'nights': nights,
                'base_price_per_night': str(property_obj.base_price_per_night),
                'total_price': str(total_price),
                'average_price_per_night': str(avg_price_per_night),
                'currency': property_obj.currency,
                'daily_breakdown': daily_prices
            })

        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
