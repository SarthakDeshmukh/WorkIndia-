from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TrainViewSet, login_view, check_availability, book_seat, get_booking_details

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'trains', TrainViewSet, basename='train')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('check_availability/', check_availability, name='check_availability'),
    path('book_seat/', book_seat, name='book_seat'),
    path('get_booking_details/', get_booking_details, name='get_booking_details'),
]