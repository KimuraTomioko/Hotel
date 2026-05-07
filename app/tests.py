from datetime import date

from django.test import TestCase

from app.models import Booking, CustomAuthenticationUser, Hotel, Review, Room
from app.serializers import BookingSerializer


class BookingAndReviewTests(TestCase):
    def setUp(self):
        self.owner = CustomAuthenticationUser.objects.create_user(
            email="owner@example.com",
            password="password",
            full_name="Owner User",
            phone="+70000000001",
        )
        self.user = CustomAuthenticationUser.objects.create_user(
            email="guest@example.com",
            password="password",
            full_name="Guest User",
            phone="+70000000002",
        )
        self.second_user = CustomAuthenticationUser.objects.create_user(
            email="second@example.com",
            password="password",
            full_name="Second Guest",
            phone="+70000000003",
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner,
            hostel_images="hotels/hotel.jpg",
            title="Test Hotel",
            description="Hotel description",
            address="Test address",
        )
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_images="rooms/room.jpg",
            type="standard",
            price_on_one_day=1000,
            description="Room description",
        )

    def test_booking_calculates_total_price(self):
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=date(2026, 6, 1),
            check_out=date(2026, 6, 4),
        )

        self.assertEqual(booking.total_price, 3000)

    def test_booking_serializer_rejects_overlapping_dates(self):
        Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=date(2026, 6, 1),
            check_out=date(2026, 6, 4),
        )

        serializer = BookingSerializer(data={
            "room": self.room.id,
            "check_in": date(2026, 6, 3),
            "check_out": date(2026, 6, 5),
        })

        self.assertFalse(serializer.is_valid())

    def test_reviews_update_hotel_rating(self):
        Review.objects.create(hotel=self.hotel, user=self.user, text="Good", score=4)
        Review.objects.create(hotel=self.hotel, user=self.second_user, text="Great", score=5)

        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.rating, 4.5)
