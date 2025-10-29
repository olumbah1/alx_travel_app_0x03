from django.core.management.base import BaseCommand
from listings.models import CustomUser, Listing, Booking, Review
from faker import Faker
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seed the database with sample data for all models'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--listings', type=int, default=20, help='Number of listings to create')
        parser.add_argument('--bookings', type=int, default=15, help='Number of bookings to create')
        parser.add_argument('--reviews', type=int, default=25, help='Number of reviews to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        fake = Faker()
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Create Users
        self.stdout.write('Creating users...')
        users = []
        for i in range(options['users']):
            email = fake.unique.email()
            username = email.split('@')[0]
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            users.append(user)
            if i % 5 == 0:
                self.stdout.write(f'Created {i+1} users...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(users)} users!'))

        # Create Listings
        self.stdout.write('Creating listings...')
        listings = []
        for i in range(options['listings']):
            listing = Listing.objects.create(
                title=fake.sentence(nb_words=4).rstrip('.'),
                description=fake.text(max_nb_chars=300),
                host=random.choice(users),
                street=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                postal_code=fake.postcode(),
                country=fake.country(),
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            listings.append(listing)
            if i % 5 == 0:
                self.stdout.write(f'Created {i+1} listings...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(listings)} listings!'))

        # Create Bookings
        self.stdout.write('Creating bookings...')
        booking_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        bookings = []
        
        for i in range(options['bookings']):
            start_date = fake.date_between(start_date='-30d', end_date='+60d')
            end_date = start_date + timedelta(days=random.randint(1, 14))
            
            booking = Booking.objects.create(
                listing_id=random.choice(listings),
                user_id=random.choice(users),
                start_date=start_date,
                end_date=end_date,
                status=random.choice(booking_statuses)
            )
            bookings.append(booking)
            if i % 5 == 0:
                self.stdout.write(f'Created {i+1} bookings...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(bookings)} bookings!'))

        # Create Reviews
        self.stdout.write('Creating reviews...')
        for i in range(options['reviews']):
            Review.objects.create(
                listing_id=random.choice(listings),
                user_id=random.choice(users),
                rating=random.randint(1, 5),
                comment=fake.paragraph(nb_sentences=random.randint(2, 5))
            )
            if i % 5 == 0:
                self.stdout.write(f'Created {i+1} reviews...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {options["reviews"]} reviews!'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== SEEDING COMPLETE ==='))
        self.stdout.write(f'Users: {CustomUser.objects.count()}')
        self.stdout.write(f'Listings: {Listing.objects.count()}')
        self.stdout.write(f'Bookings: {Booking.objects.count()}')
        self.stdout.write(f'Reviews: {Review.objects.count()}')
