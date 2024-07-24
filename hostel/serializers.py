from rest_framework import serializers
from .models import Hostel, Room, RoomDescription, Tenant, Staff, Booking, Maintenance, Facility, Payment, Notification

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'

class RoomDescriptionSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.number', read_only=True)

    class Meta:
        model = RoomDescription
        fields = ['id', 'room_number', 'sitting_room_image', 'bedroom_image', 'kitchen_image', 'bathroom_image', 'description', 'price']

class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    description = RoomDescriptionSerializer(source='roomdescription', read_only=True)  # Adjust if necessary

    class Meta:
        model = Room
        fields = ['id', 'number', 'room_type', 'image', 'hostel', 'hostel_name', 'description']

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
        fields = ['id', 'room', 'tenant', 'check_in_date', 'check_out_date']


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
