from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthRegisterViewSets, HotelViewSets, ReviewViewSets, RoomViewSets, BookingViewSets

router = DefaultRouter()
router.register('auth', AuthRegisterViewSets, 'auth')
router.register('hotels', HotelViewSets, 'hotels')
router.register('reviews', ReviewViewSets, 'reviews')
router.register('rooms', RoomViewSets, 'rooms')
router.register('bookings', BookingViewSets, 'bookings')



urlpatterns = [
    path('', include(router.urls))
]
