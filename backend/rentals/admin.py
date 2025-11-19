"""
Django Admin Configuration

Django provides a built-in admin interface (like AdminJS in Node.js)
Access at: http://localhost:8000/admin/

In Node.js, you'd need to install and configure admin panels separately:
- AdminJS (formerly AdminBro)
- Forest Admin
- React Admin
"""

from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from .models import Property, PropertyAmenity, PropertyImage, PricingRule, Booking


class PropertyAmenityInline(admin.TabularInline):
    """Inline editor for amenities (similar to nested forms in admin panels)"""
    model = PropertyAmenity
    extra = 1


class PropertyImageInline(admin.TabularInline):
    """Inline editor for images"""
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(GeoModelAdmin):
    """
    Admin interface for Properties with map widget for geolocation
    GeoModelAdmin provides a map interface for editing location
    """
    list_display = [
        'name',
        'property_type',
        'city',
        'country',
        'bedrooms',
        'bathrooms',
        'base_price_per_night',
        'created_at'
    ]
    list_filter = ['property_type', 'city', 'country', 'bedrooms', 'bathrooms']
    search_fields = ['name', 'description', 'address', 'city']
    inlines = [PropertyAmenityInline, PropertyImageInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Bookings"""
    list_display = [
        'property',
        'check_in',
        'check_out',
        'guest_name',
        'status',
        'total_price'
    ]
    list_filter = ['status', 'check_in', 'check_out']
    search_fields = ['property__name', 'guest_name', 'guest_email']


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    """Admin interface for Pricing Rules"""
    list_display = ['property', 'start_date', 'end_date', 'price_multiplier']
    list_filter = ['start_date', 'end_date']
    search_fields = ['property__name']
