from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Hostel, Room, Tenant, Staff, Booking, Maintenance, Facility, Payment, Notification
from .serializers import (
    HostelSerializer, RoomSerializer, TenantSerializer, StaffSerializer, 
    BookingSerializer, MaintenanceSerializer, FacilitySerializer, 
    PaymentSerializer, NotificationSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsTenantOrReadOnly

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse

def send_notification(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',
        {
            'type': 'notification_message',
            'message': message
        }
    )

def admin_send_notification(request):
    # Your logic to send notification
    send_notification("Admin sent a notification")
    return JsonResponse({'status': 'Notification sent'})

def user_request_requisition(request):
    # Your logic for user requisition
    send_notification("User requested a requisition")
    return JsonResponse({'status': 'Requisition requested'})


class HostelListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = HostelSerializer

    def get(self, request):
        hostels = Hostel.objects.all()
        serializer = self.serializer_class(hostels, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HostelDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = HostelSerializer

    def get_object(self, pk):
        try:
            return Hostel.objects.get(pk=pk)
        except Hostel.DoesNotExist:
            return None

    def get(self, request, pk):
        hostel = self.get_object(pk)
        if hostel is None:
            return Response({'error': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(hostel)
        return Response(serializer.data)

    def put(self, request, pk):
        hostel = self.get_object(pk)
        if hostel is None:
            return Response({'error': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(hostel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        hostel = self.get_object(pk)
        if hostel is None:
            return Response({'error': 'Hostel not found'}, status=status.HTTP_404_NOT_FOUND)
        hostel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = RoomSerializer

    def get(self, request):
        rooms = Room.objects.all()
        serializer = self.serializer_class(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = RoomSerializer

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_object(pk)
        if room is None:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(room)
        return Response(serializer.data)

    def put(self, request, pk):
        room = self.get_object(pk)
        if room is None:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        room = self.get_object(pk)
        if room is None:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TenantListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer

    def get(self, request):
        tenants = Tenant.objects.all()
        serializer = self.serializer_class(tenants, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TenantDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer

    def get_object(self, pk):
        try:
            return Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            return None

    def get(self, request, pk):
        tenant = self.get_object(pk)
        if tenant is None:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(tenant)
        return Response(serializer.data)

    def put(self, request, pk):
        tenant = self.get_object(pk)
        if tenant is None:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(tenant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tenant = self.get_object(pk)
        if tenant is None:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)
        tenant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StaffListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StaffSerializer

    def get(self, request):
        staffs = Staff.objects.all()
        serializer = self.serializer_class(staffs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StaffSerializer

    def get_object(self, pk):
        try:
            return Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return None

    def get(self, request, pk):
        staff = self.get_object(pk)
        if staff is None:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(staff)
        return Response(serializer.data)

    def put(self, request, pk):
        staff = self.get_object(pk)
        if staff is None:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(staff, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        staff = self.get_object(pk)
        if staff is None:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = BookingSerializer

    def get(self, request):
        bookings = Booking.objects.all()
        serializer = self.serializer_class(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = BookingSerializer

    def get_object(self, pk):
        try:
            return Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return None

    def get(self, request, pk):
        booking = self.get_object(pk)
        if booking is None:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(booking)
        return Response(serializer.data)

    def put(self, request, pk):
        booking = self.get_object(pk)
        if booking is None:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = self.get_object(pk)
        if booking is None:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MaintenanceListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsTenantOrReadOnly]
    serializer_class = MaintenanceSerializer

    def get(self, request):
        maintenances = Maintenance.objects.all()
        serializer = self.serializer_class(maintenances, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MaintenanceDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsTenantOrReadOnly]
    serializer_class = MaintenanceSerializer

    def get_object(self, pk):
        try:
            return Maintenance.objects.get(pk=pk)
        except Maintenance.DoesNotExist:
            return None

    def get(self, request, pk):
        maintenance = self.get_object(pk)
        if maintenance is None:
            return Response({'error': 'Maintenance not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(maintenance)
        return Response(serializer.data)

    def put(self, request, pk):
        maintenance = self.get_object(pk)
        if maintenance is None:
            return Response({'error': 'Maintenance not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(maintenance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        maintenance = self.get_object(pk)
        if maintenance is None:
            return Response({'error': 'Maintenance not found'}, status=status.HTTP_404_NOT_FOUND)
        maintenance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FacilityListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = FacilitySerializer

    def get(self, request):
        facilities = Facility.objects.all()
        serializer = self.serializer_class(facilities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FacilityDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = FacilitySerializer

    def get_object(self, pk):
        try:
            return Facility.objects.get(pk=pk)
        except Facility.DoesNotExist:
            return None

    def get(self, request, pk):
        facility = self.get_object(pk)
        if facility is None:
            return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(facility)
        return Response(serializer.data)

    def put(self, request, pk):
        facility = self.get_object(pk)
        if facility is None:
            return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(facility, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        facility = self.get_object(pk)
        if facility is None:
            return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
        facility.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = PaymentSerializer

    def get(self, request):
        payments = Payment.objects.all()
        serializer = self.serializer_class(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = PaymentSerializer

    def get_object(self, pk):
        try:
            return Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return None

    def get(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(payment)
        return Response(serializer.data)

    def put(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get(self, request):
        notifications = Notification.objects.all()
        serializer = self.serializer_class(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_object(self, pk):
        try:
            return Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return None

    def get(self, request, pk):
        notification = self.get_object(pk)
        if notification is None:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(notification)
        return Response(serializer.data)

    def put(self, request, pk):
        notification = self.get_object(pk)
        if notification is None:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(notification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        notification = self.get_object(pk)
        if notification is None:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

# Define signals for automatic notifications
@receiver(post_save, sender=Booking)
def create_booking_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f"Booking created: {instance.room.name} from {instance.start_date} to {instance.end_date}"
        )

@receiver(post_save, sender=Maintenance)
def create_maintenance_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.reported_by,
            message=f"Maintenance request created: {instance.description}"
        )