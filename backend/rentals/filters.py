"""
Django Filters for Property API

COMPARISON WITH NODE.JS:
========================

In Node.js/Express, you'd manually parse query parameters:
```javascript
app.get('/api/properties', (req, res) => {
  const { min_price, max_price, bedrooms, city, property_type } = req.query;

  let where = {};
  if (min_price) where.base_price_per_night = { [Op.gte]: min_price };
  if (max_price) where.base_price_per_night = { ...where.base_price_per_night, [Op.lte]: max_price };
  if (bedrooms) where.bedrooms = bedrooms;
  if (city) where.city = city;
  if (property_type) where.property_type = property_type;

  const properties = await Property.findAll({ where });
  res.json(properties);
});
```

Django Filter makes this automatic and type-safe!
"""

from django_filters import rest_framework as filters
from .models import Property
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q


class PropertyFilter(filters.FilterSet):
    """
    Filter class for Property queries

    This automatically generates URL query parameters:
    - /api/properties/?min_price=100&max_price=500
    - /api/properties/?bedrooms=2&bathrooms__gte=1.5
    - /api/properties/?property_type=Apartment
    - /api/properties/?city=Berlin
    - /api/properties/?amenities=WiFi,Pool
    """

    # Price range filters
    # In Node.js: WHERE base_price_per_night >= min_price AND base_price_per_night <= max_price
    min_price = filters.NumberFilter(
        field_name='base_price_per_night',
        lookup_expr='gte',  # greater than or equal
        label='Minimum price per night'
    )
    max_price = filters.NumberFilter(
        field_name='base_price_per_night',
        lookup_expr='lte',  # less than or equal
        label='Maximum price per night'
    )

    # Bedrooms and Bathrooms
    # Supports exact match and range queries
    bedrooms = filters.NumberFilter(
        field_name='bedrooms',
        lookup_expr='exact'
    )
    bedrooms__gte = filters.NumberFilter(
        field_name='bedrooms',
        lookup_expr='gte',
        label='Minimum bedrooms'
    )
    bathrooms = filters.NumberFilter(
        field_name='bathrooms',
        lookup_expr='exact'
    )
    bathrooms__gte = filters.NumberFilter(
        field_name='bathrooms',
        lookup_expr='gte',
        label='Minimum bathrooms'
    )

    # Property type filter
    # In Node.js: WHERE property_type = 'Apartment'
    property_type = filters.ChoiceFilter(
        choices=Property.PROPERTY_TYPES,
        label='Property type'
    )

    # City filter (case-insensitive contains)
    # In Node.js/Sequelize: WHERE city ILIKE '%berlin%'
    city = filters.CharFilter(
        field_name='city',
        lookup_expr='icontains',  # case-insensitive contains
        label='City'
    )

    # Country filter
    country = filters.CharFilter(
        field_name='country',
        lookup_expr='icontains',
        label='Country'
    )

    # Amenities filter (comma-separated list)
    # Usage: ?amenities=WiFi,Pool,Kitchen
    # In Node.js, you'd need to:
    # 1. Split the string
    # 2. JOIN with PropertyAmenity table
    # 3. Filter WHERE amenity IN ('WiFi', 'Pool', 'Kitchen')
    amenities = filters.CharFilter(
        method='filter_amenities',
        label='Amenities (comma-separated)'
    )

    # Max guests filter
    max_guests = filters.NumberFilter(
        field_name='max_guests',
        lookup_expr='gte',
        label='Minimum guest capacity'
    )

    # Date availability filters
    # Check if property is available for the given date range
    check_in = filters.DateFilter(
        method='filter_available_dates',
        label='Check-in date'
    )
    check_out = filters.DateFilter(
        method='filter_available_dates',
        label='Check-out date'
    )

    # Geolocation filters
    # These will be handled in the ViewSet using PostGIS queries
    latitude = filters.NumberFilter(
        method='filter_by_distance',
        label='Latitude for proximity search'
    )
    longitude = filters.NumberFilter(
        method='filter_by_distance',
        label='Longitude for proximity search'
    )
    radius = filters.NumberFilter(
        method='filter_by_distance',
        label='Radius in kilometers'
    )

    class Meta:
        model = Property
        fields = [
            'property_type',
            'city',
            'country',
            'bedrooms',
            'bathrooms',
            'max_guests',
        ]

    def filter_amenities(self, queryset, name, value):
        """
        Filter properties by amenities

        In Node.js/Sequelize:
        ```javascript
        const amenities = req.query.amenities.split(',');
        const properties = await Property.findAll({
          include: [{
            model: PropertyAmenity,
            where: { amenity: { [Op.in]: amenities } },
            required: true
          }]
        });
        ```

        Django ORM equivalent:
        """
        if not value:
            return queryset

        # Split comma-separated amenities
        amenity_list = [a.strip() for a in value.split(',')]

        # Filter properties that have ALL specified amenities
        # This uses a subquery for each amenity
        for amenity in amenity_list:
            queryset = queryset.filter(amenities__amenity__icontains=amenity)

        return queryset.distinct()

    def filter_available_dates(self, queryset, name, value):
        """
        Filter properties available for the given date range

        In Node.js:
        ```javascript
        const checkIn = req.query.check_in;
        const checkOut = req.query.check_out;

        // Find properties with NO overlapping bookings
        const unavailablePropertyIds = await Booking.findAll({
          where: {
            status: 'confirmed',
            [Op.or]: [
              { check_in: { [Op.between]: [checkIn, checkOut] } },
              { check_out: { [Op.between]: [checkIn, checkOut] } },
              {
                [Op.and]: [
                  { check_in: { [Op.lte]: checkIn } },
                  { check_out: { [Op.gte]: checkOut } }
                ]
              }
            ]
          },
          attributes: ['property_id']
        });

        const properties = await Property.findAll({
          where: {
            id: { [Op.notIn]: unavailablePropertyIds.map(b => b.property_id) }
          }
        });
        ```
        """
        # Get both check_in and check_out from request
        request = self.request
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')

        if not check_in or not check_out:
            return queryset

        # Exclude properties with overlapping bookings
        # A booking overlaps if:
        # 1. Booking check_in is between requested dates
        # 2. Booking check_out is between requested dates
        # 3. Booking completely encompasses requested dates
        overlapping_bookings = Q(
            bookings__status='confirmed'
        ) & (
            Q(bookings__check_in__lte=check_out, bookings__check_out__gte=check_in)
        )

        # Exclude properties with overlapping bookings
        return queryset.exclude(overlapping_bookings).distinct()

    def filter_by_distance(self, queryset, name, value):
        """
        This is handled in the ViewSet using PostGIS distance queries
        Just return the queryset as-is here
        """
        return queryset
