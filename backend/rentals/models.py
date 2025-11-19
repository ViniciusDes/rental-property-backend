"""
Django Models for Rental API

COMPARISON WITH NODE.JS/SEQUELIZE/TYPEORM:
========================================

In Node.js with Sequelize, you'd define models like:
```javascript
const Property = sequelize.define('Property', {
  name: { type: DataTypes.STRING, allowNull: false },
  latitude: { type: DataTypes.FLOAT, allowNull: false },
  // ... etc
});
```

In TypeORM (TypeScript):
```typescript
@Entity()
class Property {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;
  // ... etc
}
```

Django's ORM is similar but uses Python class inheritance.
Django automatically handles migrations (like Sequelize migrations or TypeORM migrations).
"""

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.contrib.gis.geos import Point
from django.utils import timezone


class Property(models.Model):
    """
    Property model - represents a rental property with geolocation.

    Node.js equivalent:
    const Property = sequelize.define('Property', { ... });
    """

    # Property Types - similar to ENUM in SQL or TypeScript
    PROPERTY_TYPES = [
        ('Apartment', 'Apartment'),
        ('House', 'House'),
        ('Condo', 'Condo'),
        ('Villa', 'Villa'),
        ('Townhouse', 'Townhouse'),
        ('Loft', 'Loft'),
        ('Studio', 'Studio'),
        ('Penthouse', 'Penthouse'),
        ('Cottage', 'Cottage'),
        ('Bungalow', 'Bungalow'),
    ]

    # Basic Information
    # In Node.js: name: { type: DataTypes.STRING, allowNull: false }
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    # Property Type with choices
    # In Node.js: property_type: { type: DataTypes.ENUM(...) }
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPES,
        db_index=True  # Index for faster filtering
    )

    # Address Information
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, db_index=True)

    # Geolocation using PostGIS PointField
    # This is SPECIAL in Django - much more powerful than storing lat/lng separately
    # In Node.js with PostGIS: you'd use raw SQL or libraries like node-postgis
    # PointField automatically creates a GEOMETRY column with spatial indexes
    location = gis_models.PointField(
        geography=True,  # Use geography type for accurate distance calculations
        srid=4326,       # WGS84 coordinate system (standard GPS coordinates)
        db_index=True    # Spatial index for fast geolocation queries
    )

    # Also store latitude and longitude separately for easy access
    # (PointField is great for queries, but these are easier to serialize)
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Property Details
    # In Node.js: bedrooms: { type: DataTypes.INTEGER, allowNull: false }
    bedrooms = models.IntegerField(db_index=True)
    bathrooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        db_index=True
    )
    max_guests = models.IntegerField()

    # Pricing
    base_price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True  # Index for price range filtering
    )
    currency = models.CharField(max_length=3, default='USD')

    # Timestamps
    # In Node.js with Sequelize: timestamps: true (automatic createdAt/updatedAt)
    # Django doesn't auto-add these, so we define them explicitly
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Database table name
        db_table = 'properties'

        # Indexes for better query performance
        # In Node.js/Sequelize: indexes: [{ fields: ['city', 'property_type'] }]
        indexes = [
            models.Index(fields=['city', 'property_type']),
            models.Index(fields=['base_price_per_night']),
            models.Index(fields=['bedrooms', 'bathrooms']),
            # Spatial index is automatically created for PointField
        ]

        # Default ordering
        # In Node.js: findAll({ order: [['created_at', 'DESC']] })
        ordering = ['-created_at']

        # Verbose names for admin interface
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        """
        String representation of the model
        Similar to toString() in JavaScript
        """
        return f"{self.name} - {self.city}"

    def save(self, *args, **kwargs):
        """
        Override save method to create Point from latitude/longitude
        Similar to Sequelize hooks: beforeCreate, beforeUpdate
        """
        if self.latitude and self.longitude:
            # Create PostGIS Point from lat/lng
            # SRID 4326 is WGS84 (standard GPS coordinate system)
            self.location = Point(self.longitude, self.latitude, srid=4326)
        super().save(*args, **kwargs)


class PropertyAmenity(models.Model):
    """
    Property Amenities - Many-to-Many relationship with Property

    Node.js equivalent with Sequelize:
    Property.hasMany(PropertyAmenity)
    PropertyAmenity.belongsTo(Property)
    """

    # Foreign Key relationship
    # In Node.js: property_id: { type: DataTypes.INTEGER, references: { model: 'Property' } }
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,  # Delete amenities when property is deleted
        related_name='amenities'   # Allows: property.amenities.all()
    )

    # Common amenities list
    AMENITY_CHOICES = [
        ('WiFi', 'WiFi'),
        ('Kitchen', 'Kitchen'),
        ('Parking', 'Parking'),
        ('Pool', 'Pool'),
        ('Gym', 'Gym'),
        ('Air Conditioning', 'Air Conditioning'),
        ('Heating', 'Heating'),
        ('TV', 'TV'),
        ('Washer', 'Washer'),
        ('Dryer', 'Dryer'),
        ('Elevator', 'Elevator'),
        ('Balcony', 'Balcony'),
        ('Pet Friendly', 'Pet Friendly'),
    ]

    amenity = models.CharField(max_length=100, db_index=True)

    class Meta:
        db_table = 'property_amenities'
        verbose_name = 'Property Amenity'
        verbose_name_plural = 'Property Amenities'
        # Prevent duplicate amenities for the same property
        unique_together = ['property', 'amenity']

    def __str__(self):
        return f"{self.property.name} - {self.amenity}"


class PropertyImage(models.Model):
    """
    Property Images

    Node.js equivalent:
    Property.hasMany(PropertyImage)
    """

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images'  # Allows: property.images.all()
    )

    # In a real app, you'd use ImageField with S3/CloudFront
    # For this example, we store URLs
    image_url = models.URLField(max_length=500)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'property_images'
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['-is_primary', 'id']  # Primary images first

    def __str__(self):
        return f"{self.property.name} - Image {self.id}"


class PricingRule(models.Model):
    """
    Dynamic Pricing Rules for different date ranges

    Similar to a rate/pricing table in a hotel booking system
    """

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='pricing_rules'
    )

    # Date range for the pricing rule
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

    # Multiplier for base price
    # e.g., 1.5 = 50% increase, 0.8 = 20% discount
    price_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0
    )

    class Meta:
        db_table = 'pricing_rules'
        verbose_name = 'Pricing Rule'
        verbose_name_plural = 'Pricing Rules'
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['property', 'start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.property.name} - {self.start_date} to {self.end_date}"


class Booking(models.Model):
    """
    Property Bookings

    This tracks when properties are unavailable.
    Important for calendar integration and availability checking.
    """

    BOOKING_STATUS = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Booking dates
    check_in = models.DateField(db_index=True)
    check_out = models.DateField(db_index=True)

    # Guest information
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)

    # Pricing
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='confirmed',
        db_index=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'check_in', 'check_out']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.property.name} - {self.check_in} to {self.check_out}"

    def is_active(self):
        """
        Check if booking is currently active
        Similar to a method in JavaScript
        """
        return self.status == 'confirmed' and self.check_in <= timezone.now().date() <= self.check_out
