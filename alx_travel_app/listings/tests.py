from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import Listing, Booking, Review, Payment

User = get_user_model()

class BookingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.host = User.objects.create_user(
            username='testhost',
            email='host@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Host'
        )
        
        self.guest = User.objects.create_user(
            username='testguest',
            email='guest@example.com',
            password='testpass123',
            first_name='Guest',
            last_name='User'
        )
        
        self.listing = Listing.objects.create(
            title='Test Listing',
            description='Test Description',
            host=self.host,
            street='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
    
    def test_create_booking_authenticated(self):
        """Test creating a booking with authentication"""
        self.client.force_authenticate(user=self.guest)
    
        start_date = timezone.now()
        end_date = start_date + timedelta(days=5)
    
        response = self.client.post('/api/bookings/', {
            'listing_id': str(self.listing.listing_id),
            'user_id': str(self.guest.user_id),  # Use CustomUser's user_id UUID
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'status': 'pending'
        },  format='json')
    
        if response.status_code != 201:
            print(f"Response data: {response.data}")
    
        self.assertIn(response.status_code, [200, 201])
    
    def test_list_bookings_authenticated(self):
        """Test listing bookings for authenticated user"""
        self.client.force_authenticate(user=self.guest)
        
        response = self.client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_cannot_create_booking(self):
        """Test that unauthenticated users can't create bookings"""
        response = self.client.post('/api/bookings/', {})
        
        self.assertIn(response.status_code, [401, 403])
    
    def test_booking_created(self):
        """Test that booking is created in database"""
        start_date = timezone.now()
        end_date = start_date + timedelta(days=5)
        
        booking = Booking.objects.create(
            listing_id=self.listing,
            user_id=self.guest,
            start_date=start_date,
            end_date=end_date,
            status=Booking.Status.PENDING
        )
        
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.status, 'pending')