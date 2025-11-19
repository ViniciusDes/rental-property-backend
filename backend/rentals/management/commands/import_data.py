"""
Django Management Command to Import Data from SQLite

COMPARISON WITH NODE.JS:
========================

In Node.js, you'd create a script file:
```javascript
// scripts/import-data.js
const sqlite3 = require('sqlite3');
const { Property, Booking } = require('./models');

async function importData() {
  const db = new sqlite3.Database('sample-data.db');

  // Read from SQLite
  const properties = await db.all('SELECT * FROM properties');

  // Insert into PostgreSQL
  for (const prop of properties) {
    await Property.create({
      name: prop.name,
      latitude: prop.latitude,
      // ... etc
    });
  }
}

importData();
```

Then run: node scripts/import-data.js

In Django, we create a management command that can be run with:
python manage.py import_data
"""

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from backend.rentals.models import (
    Property,
    PropertyAmenity,
    PropertyImage,
    PricingRule,
    Booking
)
import sqlite3
from datetime import datetime


class Command(BaseCommand):
    help = 'Import data from sample-data.db SQLite database to PostgreSQL'

    def add_arguments(self, parser):
        """
        Add command line arguments
        Similar to argparse in Python or commander in Node.js
        """
        parser.add_argument(
            '--db-path',
            type=str,
            default='sample-data.db',
            help='Path to SQLite database file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        """
        Main command logic
        Similar to main() function in a Node.js script
        """
        db_path = options['db_path']
        clear_data = options['clear']

        self.stdout.write(self.style.SUCCESS(f'Starting data import from {db_path}'))

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Booking.objects.all().delete()
            PricingRule.objects.all().delete()
            PropertyImage.objects.all().delete()
            PropertyAmenity.objects.all().delete()
            Property.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared'))

        # Connect to SQLite database
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = conn.cursor()

            # Import Properties
            self.import_properties(cursor)

            # Import Property Amenities
            self.import_amenities(cursor)

            # Import Property Images
            self.import_images(cursor)

            # Import Pricing Rules
            self.import_pricing_rules(cursor)

            # Import Bookings
            self.import_bookings(cursor)

            conn.close()

            self.stdout.write(self.style.SUCCESS('Data import completed successfully!'))

        except sqlite3.Error as e:
            self.stdout.write(self.style.ERROR(f'SQLite error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))

    def import_properties(self, cursor):
        """Import properties from SQLite to PostgreSQL"""
        self.stdout.write('Importing properties...')

        cursor.execute('SELECT * FROM properties')
        properties = cursor.fetchall()

        property_map = {}  # Map old IDs to new objects

        for row in properties:
            # Create Property object
            # Django automatically handles ID generation
            property_obj = Property(
                name=row['name'],
                description=row['description'],
                property_type=row['property_type'],
                address=row['address'],
                city=row['city'],
                country=row['country'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                bedrooms=row['bedrooms'],
                bathrooms=row['bathrooms'],
                max_guests=row['max_guests'],
                base_price_per_night=row['base_price_per_night'],
                currency=row['currency'],
            )

            # The save() method will automatically create the PostGIS Point
            # from latitude/longitude (see models.py save() override)
            property_obj.save()

            # Store mapping for foreign keys
            property_map[row['id']] = property_obj

        self.stdout.write(
            self.style.SUCCESS(f'Imported {len(properties)} properties')
        )

        # Store for use in other import methods
        self.property_map = property_map

    def import_amenities(self, cursor):
        """Import property amenities"""
        self.stdout.write('Importing amenities...')

        cursor.execute('SELECT * FROM property_amenities')
        amenities = cursor.fetchall()

        amenity_objects = []
        for row in amenities:
            property_obj = self.property_map.get(row['property_id'])
            if property_obj:
                amenity_objects.append(
                    PropertyAmenity(
                        property=property_obj,
                        amenity=row['amenity']
                    )
                )

        # Bulk create for better performance
        # In Node.js/Sequelize: PropertyAmenity.bulkCreate(amenities)
        PropertyAmenity.objects.bulk_create(amenity_objects)

        self.stdout.write(
            self.style.SUCCESS(f'Imported {len(amenity_objects)} amenities')
        )

    def import_images(self, cursor):
        """Import property images"""
        self.stdout.write('Importing property images...')

        cursor.execute('SELECT * FROM property_images')
        images = cursor.fetchall()

        image_objects = []
        for row in images:
            property_obj = self.property_map.get(row['property_id'])
            if property_obj:
                image_objects.append(
                    PropertyImage(
                        property=property_obj,
                        image_url=row['image_url'],
                        is_primary=bool(row['is_primary'])
                    )
                )

        PropertyImage.objects.bulk_create(image_objects)

        self.stdout.write(
            self.style.SUCCESS(f'Imported {len(image_objects)} images')
        )

    def import_pricing_rules(self, cursor):
        """Import pricing rules"""
        self.stdout.write('Importing pricing rules...')

        cursor.execute('SELECT * FROM pricing_rules')
        rules = cursor.fetchall()

        rule_objects = []
        for row in rules:
            property_obj = self.property_map.get(row['property_id'])
            if property_obj:
                rule_objects.append(
                    PricingRule(
                        property=property_obj,
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        price_multiplier=row['price_multiplier']
                    )
                )

        PricingRule.objects.bulk_create(rule_objects)

        self.stdout.write(
            self.style.SUCCESS(f'Imported {len(rule_objects)} pricing rules')
        )

    def import_bookings(self, cursor):
        """Import bookings"""
        self.stdout.write('Importing bookings...')

        cursor.execute('SELECT * FROM bookings')
        bookings = cursor.fetchall()

        booking_objects = []
        for row in bookings:
            property_obj = self.property_map.get(row['property_id'])
            if property_obj:
                booking_objects.append(
                    Booking(
                        property=property_obj,
                        check_in=row['check_in'],
                        check_out=row['check_out'],
                        guest_name=row['guest_name'],
                        guest_email=row['guest_email'],
                        total_price=row['total_price'],
                        status=row['status']
                    )
                )

        Booking.objects.bulk_create(booking_objects)

        self.stdout.write(
            self.style.SUCCESS(f'Imported {len(booking_objects)} bookings')
        )
