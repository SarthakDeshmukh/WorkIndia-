# railway/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Train, Booking

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ['id', 'name', 'source', 'destination', 'total_seats', 'available_seats']


class BookingSerializer(serializers.ModelSerializer):
    train = TrainSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'train', 'seats_booked', 'created_at']
