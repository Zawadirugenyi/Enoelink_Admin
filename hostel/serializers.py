from rest_framework import serializers
from .models import Booking, Room, Hostel, RoomDescription, Tenant, Staff, Maintenance, Facility, Payment, Notification
from .models import Notification, Payment, Request
from django.utils.dateparse import parse_date

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'


class RoomDescriptionSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.number', read_only=True)
    hostel_name = serializers.CharField(source='room.hostel.name')

    class Meta:
        model = RoomDescription
        fields = ['room_number', 'hostel_name', 'sitting_room_image', 'bedroom_image', 'kitchen_image', 'bathroom_image', 'description', 'price']


class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    description = RoomDescriptionSerializer(source='roomdescription', read_only=True)

    class Meta:
        model = Room
        fields = '__all__'


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        room = data.get('room')
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        if not room or not check_in_date or not check_out_date:
            raise serializers.ValidationError("Room, check-in date, and check-out date are required.")

        if check_in_date >= check_out_date:
            raise serializers.ValidationError("Check-out date must be after check-in date.")

        existing_bookings = Booking.objects.filter(
            room=room,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        )

        if existing_bookings.exists():
            raise serializers.ValidationError("This room is already booked for the selected dates.")

        return data

    def create(self, validated_data):
        booking = super().create(validated_data)
        room = booking.room
        room.status = False  # Mark room as booked
        room.save()
        return booking
    

class MaintenanceSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())  # Use PrimaryKeyRelatedField for room

    class Meta:
        model = Maintenance
        fields = ['id', 'room', 'type', 'otherType', 'description', 'completed']


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'