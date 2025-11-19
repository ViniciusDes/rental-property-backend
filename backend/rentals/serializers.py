"""
Django REST Framework Serializers

COMPARISON WITH NODE.JS:
========================

In Node.js/Express, you might manually format responses:
```javascript
const formatProperty = (property) => ({
  id: property.id,
  name: property.name,
  price: parseFloat(property.price),
  // ... etc
});

res.json(properties.map(formatProperty));
```

Or with a library like class-transformer in TypeScript:
```typescript
class PropertyDTO {
  @Expose() id: number;
  @Expose() name: string;
  // ... etc
}
```

Django REST Framework serializers handle:
1. Converting models to JSON (serialization)
2. Validating incoming data (if we had POST/PUT)
3. Nested relationships
4. Custom fields
"""

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Property, PropertyAmenity, PropertyImage, PricingRule, Booking
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from datetime import date


class PropertyImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Property Images

    In Node.js, this is like a nested object in your JSON response
    """

    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'is_primary']


class PropertyAmenitySerializer(serializers.ModelSerializer):
    """
    Serializer for Property Amenities

    Returns just the amenity name for cleaner API responses
    """

    class Meta:
        model = PropertyAmenity
        fields = ['amenity']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookings
    Used to show unavailable dates in the calendar
    """

    class Meta:
        model = Booking
        fields = ['id', 'check_in', 'check_out', 'status']


class PropertyListSerializer(serializers.ModelSerializer):
    """
    Serializer for Property List View

    Similar to a DTO (Data Transfer Object) in Node.js/TypeScript
    Shows summary information without all the details
    """

    # SerializerMethodField allows custom computed fields
    # Similar to adding a getter method in JavaScript classes
    amenities = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'property_type',
            'city',
            'country',
            'latitude',
            'longitude',
            'bedrooms',
            'bathrooms',
            'max_guests',
            'base_price_per_night',
            'currency',
            'amenities',
            'primary_image',
            'distance',  # Only present when filtering by location
        ]

    def get_amenities(self, obj):
        """
        Get list of amenity names

        In Node.js/Sequelize with eager loading:
        include: [{ model: PropertyAmenity, attributes: ['amenity'] }]
        then: property.amenities.map(a => a.amenity)
        """
        return [amenity.amenity for amenity in obj.amenities.all()]

    def get_primary_image(self, obj):
        """
        Get primary image URL

        In Node.js:
        const primaryImage = property.images.find(img => img.is_primary);
        return primaryImage?.image_url || null;
        """
        primary = obj.images.filter(is_primary=True).first()
        return primary.image_url if primary else None

    def get_distance(self, obj):
        """
        Get distance in kilometers (only present when geolocation filtering is used)

        In Node.js:
        if (property.distance) {
          return parseFloat(property.distance / 1000); // Convert meters to km
        }
        return null;
        """
        if hasattr(obj, 'distance') and obj.distance is not None:
            return round(obj.distance.km, 2)  # Convert to kilometers and round to 2 decimals
        return None


class PropertyDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Property Detail View

    Shows complete information including all related data
    Similar to eager loading all relations in Sequelize:
    Property.findOne({ include: [PropertyAmenity, PropertyImage, Booking] })
    """

    # Nested serializers for related models
    # In Node.js, this is achieved with JOIN queries and object mapping
    amenities = serializers.SerializerMethodField()
    images = PropertyImageSerializer(many=True, read_only=True)
    available_dates = serializers.SerializerMethodField()
    unavailable_dates = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'name',
            'description',
            'property_type',
            'address',
            'city',
            'country',
            'latitude',
            'longitude',
            'bedrooms',
            'bathrooms',
            'max_guests',
            'base_price_per_night',
            'currency',
            'amenities',
            'images',
            'available_dates',
            'unavailable_dates',
            'created_at',
            'updated_at',
        ]

    def get_amenities(self, obj):
        """Get list of amenity names"""
        return [amenity.amenity for amenity in obj.amenities.all()]

    def get_unavailable_dates(self, obj):
        """
        Get list of booked date ranges

        In Node.js:
        const bookings = await Booking.findAll({
          where: {
            property_id: property.id,
            status: 'confirmed'
          }
        });
        return bookings.map(b => ({ check_in: b.check_in, check_out: b.check_out }));
        """
        confirmed_bookings = obj.bookings.filter(status='confirmed')
        return [
            {
                'check_in': booking.check_in.isoformat(),
                'check_out': booking.check_out.isoformat(),
            }
            for booking in confirmed_bookings
        ]

    def get_available_dates(self, obj):
        """
        Calculate available dates (simplified example)

        In a real app, you'd implement complex availability logic
        For now, we just return a message
        """
        return {
            'message': 'Check unavailable_dates for booked periods',
            'note': 'All other dates are potentially available'
        }


class PropertyGeoJSONSerializer(GeoFeatureModelSerializer):
    """
    GeoJSON serializer for map visualization

    GeoJSON is a standard format for geographic data:
    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [lng, lat] },
          "properties": { "name": "...", "price": ... }
        }
      ]
    }

    In Node.js, you'd manually construct this format:
    const geoJSON = {
      type: 'FeatureCollection',
      features: properties.map(p => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [p.longitude, p.latitude] },
        properties: { name: p.name, price: p.base_price_per_night }
      }))
    };
    """

    class Meta:
        model = Property
        geo_field = 'location'  # The PostGIS PointField
        fields = [
            'id',
            'name',
            'property_type',
            'base_price_per_night',
            'bedrooms',
            'bathrooms',
        ]
