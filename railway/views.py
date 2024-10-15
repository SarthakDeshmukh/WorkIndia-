# railway/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Train, Booking
from .serializers import UserSerializer, TrainSerializer, BookingSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .permissions import IsAdminWithAPIKey  # Custom permission class
import json

API_KEY = '1234'  # Replace with a more secure key in production


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TrainViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin to manage trains.
    Protected with API Key and admin privileges.
    """
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = [IsAdminWithAPIKey]  # Custom permission


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login view that returns an authentication token.
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_availability(request):
    """
    Check seat availability between source and destination.
    """
    try:
        source = request.data.get('source')
        destination = request.data.get('destination')

        if not source or not destination:
            return Response({'error': 'Source and destination are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        trains = Train.objects.filter(source=source, destination=destination)
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def book_seat(request):
    """
    Book seats on a specific train.
    Handles race conditions using transactions and row-level locking.
    """
    try:
        train_id = request.data.get('train_id')
        seats = request.data.get('seats')

        if not train_id or not seats:
            return Response({'error': 'Train ID and number of seats are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            seats = int(seats)
            if seats <= 0:
                raise ValueError
        except ValueError:
            return Response({'error': 'Number of seats must be a positive integer.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        with transaction.atomic():
            # Lock the train row to prevent race conditions
            train = Train.objects.select_for_update().get(id=train_id)
            if train.available_seats >= seats:
                train.available_seats -= seats
                train.save()
                Booking.objects.create(user=user, train=train, seats_booked=seats)
                return Response({'message': 'Booking successful.'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Not enough seats available.'},
                                status=status.HTTP_400_BAD_REQUEST)
    except Train.DoesNotExist:
        return Response({'error': 'Train not found.'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_booking_details(request):
    """
    Retrieve booking details for the authenticated user.
    """
    try:
        user = request.user
        bookings = Booking.objects.filter(user=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
