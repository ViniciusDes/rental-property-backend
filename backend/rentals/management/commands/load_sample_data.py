"""
Management command to load sample data from SQLite to PostgreSQL
Usage: python manage.py load_sample_data
"""
import sqlite3
import os
from django.core.management.base import BaseCommand
from backend.rentals.models import Property, PropertyImage, PropertyAmenity, PricingRule, Booking


class Command(BaseCommand):
    help = 'Load sample data from sample-data.db into PostgreSQL database'

    def handle(self, *args, **options):
        # Check if data already exists
        if Property.objects.exists():
            self.stdout.write(
                self.style.WARNING('Database already contains data. Skipping sample data load.')
            )
            return

        sample_db_path = os.path.join(os.path.dirname(__file__), '../../../..', 'sample-data.db')

        if not os.path.exists(sample_db_path):
            self.stdout.write(
                self.style.ERROR(f'Sample data file not found at {sample_db_path}')
            )
            return

        self.stdout.write('Loading sample data from sample-data.db...')

        try:
            # Connect to SQLite database
            sqlite_conn = sqlite3.connect(sample_db_path)
            sqlite_conn.row_factory = sqlite3.Row
            cursor = sqlite_conn.cursor()

            # Load properties
            cursor.execute('SELECT * FROM properties')
            properties = cursor.fetchall()

            for row in properties:
                Property.objects.create(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] if row['description'] else '',
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
                    currency=row['currency'] if row['currency'] else 'USD',
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )

            self.stdout.write(
                self.style.SUCCESS(f'Loaded {len(properties)} properties')
            )

            # Load property images
            cursor.execute('SELECT * FROM property_images')
            images = cursor.fetchall()

            for row in images:
                PropertyImage.objects.create(
                    id=row['id'],
                    property_id=row['property_id'],
                    image_url=row['image_url'],
                    is_primary=bool(row['is_primary'])
                )

            self.stdout.write(
                self.style.SUCCESS(f'Loaded {len(images)} property images')
            )

            # Load property amenities
            cursor.execute('SELECT * FROM property_amenities')
            amenities = cursor.fetchall()

            for row in amenities:
                PropertyAmenity.objects.create(
                    id=row['id'],
                    property_id=row['property_id'],
                    amenity=row['amenity']
                )

            self.stdout.write(
                self.style.SUCCESS(f'Loaded {len(amenities)} property amenities')
            )

            # Load pricing rules
            cursor.execute('SELECT * FROM pricing_rules')
            pricing_rules = cursor.fetchall()

            for row in pricing_rules:
                PricingRule.objects.create(
                    id=row['id'],
                    property_id=row['property_id'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    price_multiplier=row['price_multiplier']
                )

            self.stdout.write(
                self.style.SUCCESS(f'Loaded {len(pricing_rules)} pricing rules')
            )

            # Load bookings
            cursor.execute('SELECT * FROM bookings')
            bookings = cursor.fetchall()

            for row in bookings:
                Booking.objects.create(
                    id=row['id'],
                    property_id=row['property_id'],
                    guest_name=row['guest_name'] if row['guest_name'] else '',
                    guest_email=row['guest_email'] if row['guest_email'] else '',
                    check_in=row['check_in'],
                    check_out=row['check_out'],
                    total_price=row['total_price'] if row['total_price'] else 0,
                    status=row['status'] if row['status'] else 'confirmed',
                    created_at=row['created_at']
                )

            self.stdout.write(
                self.style.SUCCESS(f'Loaded {len(bookings)} bookings')
            )

            sqlite_conn.close()

            self.stdout.write(
                self.style.SUCCESS('Successfully loaded all sample data!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading sample data: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
            raise
