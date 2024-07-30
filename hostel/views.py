# views.py
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404
import requests
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Room, Booking
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Room, Booking
from .serializers import BookingSerializer
import datetime
import base64
from django.http import JsonResponse
from django.views import View
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import lipa_na_mpesa_online
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (
    Room, RoomDescription, Hostel, Tenant, Staff, Booking,
    Maintenance, Facility, Payment, Notification
)
from .serializers import (
    RoomSerializer, RoomDescriptionSerializer, HostelSerializer,
    TenantSerializer, StaffSerializer, BookingSerializer,
    MaintenanceSerializer, FacilitySerializer, PaymentSerializer,
    NotificationSerializer
)

from django.core.mail import send_mail

def admin_send_notification(subject, message, recipient_list):
    """
    Sends an email notification to specified recipients.
    """
    send_mail(subject, message, 'admin@example.com', recipient_list)

def user_request_requisition(request):
    """
    Handle user requisition request logic here.
    """
   
    return HttpResponse("User requisition request handled successfully.")





# Hostel views
    
class HostelListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    


# Room views

class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = RoomSerializer

    def get(self, request):
        hostel_name = request.query_params.get('hostel__name', None)
        rooms = Room.objects.all()
        if hostel_name:
            rooms = rooms.filter(hostel__name=hostel_name)
        serializer = self.serializer_class(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomAvailabilityCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_number, hostel_id):
        room = get_object_or_404(Room, number=room_number, hostel_id=hostel_id)
        is_booked = Booking.objects.filter(room=room).exists()
        return JsonResponse({'is_booked': is_booked})


def available_rooms_view(request):
    available_rooms = Room.objects.filter(is_booked=False)
    return render(request, 'available_rooms.html', {'rooms': available_rooms})


def check_room_availability(request):
    room_id = request.GET.get('room_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not room_id or not start_date or not end_date:
        return JsonResponse({'error': 'Missing parameters.'}, status=400)

    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    overlapping_bookings = Booking.objects.filter(
        room_id=room_id,
        check_out_date__gte=start_date,
        check_in_date__lte=end_date
    )

    available = not overlapping_bookings.exists()

    return JsonResponse({'available': available})



from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Booking)
def update_room_status_on_booking_delete(sender, instance, **kwargs):
    room = instance.room
    # Check if there are any remaining bookings for this room
    if not Booking.objects.filter(room=room, check_out_date__gt=timezone.now()).exists():
        room.status = True  # Mark room as available
        room.save()


class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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


class RoomDetailByNumberView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = RoomSerializer

    def get(self, request, room_number):
        try:
            room = Room.objects.get(number=room_number)
            serializer = self.serializer_class(room)
            return Response(serializer.data)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)



# Room description views
      


def room_description(request, room_number):
    try:
        description = RoomDescription.objects.get(room_number=room_number)
        data = {
            'description': description.description,
            'capacity': description.capacity,
            'price': description.price,
            'images': [img.image.url for img in description.images.all()],
        }
        return JsonResponse(data)
    except RoomDescription.DoesNotExist:
        return JsonResponse({'error': 'Room description not found'}, status=404)

        
class RoomDescriptionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = RoomDescriptionSerializer

    def get(self, request):
        room_descriptions = RoomDescription.objects.all()
        serializer = self.serializer_class(room_descriptions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class RoomDescriptionView(APIView):
    def get(self, request, room_number, hostel_id):
        try:
            room_description = RoomDescription.objects.get(room_number=room_number, hostel_id=hostel_id)
            serializer = RoomDescriptionSerializer(room_description)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RoomDescription.DoesNotExist:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        
class RoomDescriptionDetailView(APIView):
    serializer_class = RoomDescriptionSerializer

    def get(self, request, room_number, hostel_id):
        try:
            room = Room.objects.get(number=room_number, hostel_id=hostel_id)
            room_description = RoomDescription.objects.get(room=room)
            serializer = self.serializer_class(room_description)
            return Response(serializer.data)
        except RoomDescription.DoesNotExist:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        


from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RoomDescription
from .serializers import RoomDescriptionSerializer

class RoomDescriptionView(APIView):
    def get(self, request):
        room_number = request.query_params.get('room__number')
        hostel_name = request.query_params.get('hostel__name')
        
        if not room_number or not hostel_name:
            return Response({"error": "room__number and hostel__name are required parameters"}, status=400)
        
        room_description = get_object_or_404(RoomDescription, room__number=room_number, hostel__name=hostel_name)
        serializer = RoomDescriptionSerializer(room_description)
        return Response(serializer.data)



class RoomDescriptionDetailView(APIView):
    serializer_class = RoomDescriptionSerializer

    def get_object(self, room_number, hostel_id):
        try:
            room = Room.objects.get(number=room_number, hostel_id=hostel_id)
            return RoomDescription.objects.get(room=room)
        except Room.DoesNotExist:
            return None
        except RoomDescription.DoesNotExist:
            return None

    def get(self, request, room_number, hostel_id):
        room_description = self.get_object(room_number, hostel_id)
        if room_description is None:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(room_description)
        return Response(serializer.data)

    def put(self, request, room_number, hostel_id):
        room_description = self.get_object(room_number, hostel_id)
        if room_description is None:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(room_description, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_number, hostel_id):
        room_description = self.get_object(room_number, hostel_id)
        if room_description is None:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        room_description.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# Tenant views
    
class TenantListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]

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
       

    def get_object(self, pk,  format=None):
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


# Staff views
    
class StaffListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = StaffSerializer

    def get(self, request):
        staff = Staff.objects.all()
        serializer = self.serializer_class(staff, many=True)
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


# Booking views
      

class BookingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Room, Booking

class RoomAvailabilityCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_number, hostel_id):
        room = get_object_or_404(Room, number=room_number, hostel_id=hostel_id)
        is_booked = Booking.objects.filter(room=room).exists()
        return JsonResponse({'is_booked': is_booked})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    data = request.data
    room_id = data.get('room')
    tenant_id = data.get('tenant')
    check_in_date = data.get('check_in_date')
    check_out_date = data.get('check_out_date')

    try:
        room = Room.objects.get(id=room_id)
        if room.is_booked:
            return Response({'detail': 'This room is already booked.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking = Booking.objects.create(
            room=room,
            tenant_id=tenant_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        
        room.is_booked = True
        room.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Room.DoesNotExist:
        return Response({'detail': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    



class AvailableRoomsList(generics.ListAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        check_in_date = self.request.query_params.get('check_in_date')
        check_out_date = self.request.query_params.get('check_out_date')

        if check_in_date and check_out_date:
            # Convert to date objects
            check_in_date = timezone.datetime.strptime(check_in_date, "%Y-%m-%d").date()
            check_out_date = timezone.datetime.strptime(check_out_date, "%Y-%m-%d").date()

            # Get booked room IDs
            booked_rooms = Booking.objects.filter(
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            ).values_list('room_id', flat=True)

            # Exclude booked rooms from available rooms
            return Room.objects.exclude(id__in=booked_rooms).exclude(is_booked=True)
        else:
            return Room.objects.exclude(is_booked=True)

def create_booking(room_id, tenant_id, check_in_date, check_out_date):
    room = Room.objects.get(id=room_id)
    if not room.is_booked:
        Booking.objects.create(
            room=room,
            tenant_id=tenant_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )
        room.is_booked = True
        room.save()
    else:
        raise ValueError("Room is already booked")


def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        tenant_id = request.POST.get('tenant_id')
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')

        room = get_object_or_404(Room, id=room_id)
        tenant = get_object_or_404(Tenant, id=tenant_id)

        booking = Booking.objects.create(
            room=room,
            tenant=tenant,
            check_in_date=check_in_date,
            check_out_date=check_out_date
        )

        room.is_booked = True
        room.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


def available_rooms(request):
    available_rooms = Room.objects.filter(is_booked=False)

    hostel_name = request.GET.get('hostel__name', '')
    rooms = Room.objects.filter(hostel__name=hostel_name)
    room_data = list(rooms.values('id', 'number', 'room_type', 'image'))
    return JsonResponse(room_data, safe=False)


class AvailableRoomsListView(generics.ListAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        hostel_name = self.request.query_params.get('hostel__name')
        if hostel_name:
            return Room.objects.filter(hostel__name=hostel_name, is_available=True)
        return Room.objects.filter(is_available=True)


class BookingDetailView(APIView):
   
    permission_classes = [IsAuthenticated]
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


def delete_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        room = booking.room
        booking.delete()

        # Update room status
        if not Booking.objects.filter(
            room=room,
            check_out_date__gt=timezone.now()
        ).exists():
            room.status = True
            room.save()

        return JsonResponse({'message': 'Booking deleted and room status updated.'})
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found.'}, status=404)

    



 # Maintenance views   

class MaintenanceListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = MaintenanceSerializer

    def get_object(self, pk):
        try:
            return Maintenance.objects.get(pk=pk)
        except Maintenance.DoesNotExist:
            return None

    def get(self, request, pk):
        maintenance = self.get_object(pk)
        if maintenance is None:
            return Response({'error': 'Maintenance record not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(maintenance)
        return Response(serializer.data)

    def put(self, request, pk):
        maintenance = self.get_object(pk)
        if maintenance is None:
            return Response({'error': 'Maintenance record not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(maintenance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        maintenance = self.get_object(pk)
        if maintenance is None:
            return Response({'error': 'Maintenance record not found'}, status=status.HTTP_404_NOT_FOUND)
        maintenance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






# Facility views
    
class FacilityListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    



# Payment views
    
class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = PaymentSerializer

    def get_object(self, pk):
        try:
            return Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return None

    def get(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(payment)
        return Response(serializer.data)

    def put(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payment = self.get_object(pk)
        if payment is None:
            return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




# Notifi views
    
class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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
    permission_classes = [IsAuthenticated, IsAdminUser]
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





CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
SHORTCODE = 'YOUR_SHORTCODE'
LIPA_NA_MPESA_ONLINE_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
LIPA_NA_MPESA_ONLINE_CALLBACK_URL = 'YOUR_CALLBACK_URL'

def get_mpesa_access_token():
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    try:
        response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        print("Access Token Request URL:", api_url)  # Debugging line
        print("Access Token Request Headers:", response.request.headers)  # Debugging line
        print("Access Token Response Status Code:", response.status_code)  # Debugging line
        print("Access Token Response Text:", response.text)  # Debugging line
        response.raise_for_status()  # Raise an error if the request was unsuccessful
        json_response = response.json()
        my_access_token = json_response['access_token']
        return my_access_token
    except requests.exceptions.RequestException as e:
        print("Access Token Request Failed:", e)  # Debugging line
        return None

def lipa_na_mpesa_online(phone_number, amount, account_reference, transaction_desc):
    access_token = get_mpesa_access_token()
    if not access_token:
        return {'error': 'Failed to obtain access token'}
    
    api_url = LIPA_NA_MPESA_ONLINE_URL
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f'{SHORTCODE}{LIPA_NA_MPESA_ONLINE_CALLBACK_URL}{timestamp}'.encode()).decode('utf-8')
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": LIPA_NA_MPESA_ONLINE_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    try:
        print("STK Push Request Payload:", payload)  # Debugging line
        response = requests.post(api_url, json=payload, headers=headers)
        print("Lipa na Mpesa Response Status Code:", response.status_code)  # Debugging line
        print("Lipa na Mpesa Response Text:", response.text)  # Debugging line
        response.raise_for_status()  # Raise an error if the request was unsuccessful
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Lipa na Mpesa Request Failed:", e)  # Debugging line
        return {'error': str(e)}

@method_decorator(csrf_exempt, name='dispatch')
class MpesaPaymentView(View):
    def post(self, request, *args, **kwargs):
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        account_reference = request.POST.get('account_reference')
        transaction_desc = request.POST.get('transaction_desc')

        response = lipa_na_mpesa_online(phone_number, amount, account_reference, transaction_desc)
        return JsonResponse(response)

@method_decorator(csrf_exempt, name='dispatch')
class MpesaCallbackView(View):
    def post(self, request, *args, **kwargs):
        mpesa_body = request.body.decode('utf-8')
        print(mpesa_body)  # For debugging
        # Process the callback data as required
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
import base64
import json
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def mpesa_payment(request):
    phone_number = request.data.get('phone_number')
    amount = request.data.get('amount')
    account_reference = request.data.get('account_reference')
    transaction_desc = request.data.get('transaction_desc')

    if not all([phone_number, amount, account_reference, transaction_desc]):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    # Get access token
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(access_token_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    access_token = response.json().get('access_token')

    # Prepare the payment request
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode('utf-8')
    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': phone_number,
        'CallBackURL': 'https://yourdomain.com/api/payments/mpesa/callback/',
        'AccountReference': account_reference,
        'TransactionDesc': transaction_desc
    }

    payment_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(payment_url, json=payload, headers=headers)

    if response.status_code == 200:
        return JsonResponse({'message': 'Payment processed successfully'})
    else:
        return JsonResponse({'error': 'Payment processing failed'}, status=500)
