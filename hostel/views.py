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

from django.shortcuts import render
from hostel.models import Hostel  # Ensure the correct model is imported
from hostel.models import Tenant  # Ensure the correct model is imported
from hostel.models import Booking  # Ensure the correct model is imported

def dashboard_view(request):
    # Get the counts from the database
    number_of_hostels = Hostel.objects.count()
    number_of_bookings = Booking.objects.count()
    number_of_tenants = Tenant.objects.count()  # Count tenants

    # Pass the counts into the template context
    context = {
        'number_of_hostels': number_of_hostels,
        'number_of_bookings': number_of_bookings,
        'number_of_tenants': number_of_tenants,  # Include tenant count
    }

    # Render the admin index page with the context data
    return render(request, 'admin/index.html', context)  # Adjust path if needed

from rest_framework.permissions import IsAuthenticated


class HostelListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HostelSerializer
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
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer

    def get(self, request):
        hostel_name = request.query_params.get('hostel__name', None)
        rooms = Room.objects.all()
        if hostel_name:
            rooms = rooms.filter(hostel__name=hostel_name)
        serializer = self.serializer_class(rooms, many=True)
        print(rooms)
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated] 
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
    
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Tenant
from .serializers import TenantSerializer
from django.http import JsonResponse

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

    def get_tenant_by_name(self, name):
        try:
            return Tenant.objects.get(name=name)
        except Tenant.DoesNotExist:
            return None


class TenantCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name', '')
        
        if name:
            tenant = self.get_tenant_by_name(name)
            if tenant:
                serializer = TenantSerializer(tenant)
                return Response({'exists': True, 'tenant': serializer.data})
            return Response({'exists': False}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    def get_tenant_by_name(self, name):
        try:
            return Tenant.objects.get(name=name)
        except Tenant.DoesNotExist:
            return None


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



class TenantBookingListView(View):
    def get(self, request, *args, **kwargs):
        tenant_id = request.GET.get('tenant_id')
        if not tenant_id:
            return JsonResponse({'error': 'Tenant ID is required'}, status=400)

        try:
            bookings = Booking.objects.filter(tenant_id=tenant_id)
            bookings_data = list(bookings.values('room__number', 'check_in_date', 'check_out_date'))
            return JsonResponse({'bookings': bookings_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



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
    permission_classes = [IsAuthenticated]
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

    




from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Maintenance, Room
from .serializers import MaintenanceSerializer

class MaintenanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceSerializer

    def get(self, request):
        maintenances = Maintenance.objects.all()
        serializer = self.serializer_class(maintenances, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Convert request.data to a mutable dictionary
        data = dict(request.data)
        
        room_number = data.get('room_number')
        try:
            room = Room.objects.get(number=room_number)
        except Room.DoesNotExist:
            return Response({"error": "Room with the specified number does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Add the room ID to the data dictionary
        data['room'] = room.id
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MaintenanceDetailView(APIView):
    permission_classes = [IsAuthenticated]
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
            # If the `completed` status is updated, the signal will handle the notification.
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Facility, FacilityRegistration, Tenant
from .serializers import FacilitySerializer, FacilityRegistrationSerializer
from rest_framework.decorators import api_view


class FacilityListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FacilitySerializer

    # Retrieve the list of all facilities
    def get(self, request):
        facilities = Facility.objects.all()
        serializer = self.serializer_class(facilities, many=True)
        return Response(serializer.data)

    # Create a new facility
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacilityDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FacilitySerializer

    # Helper method to retrieve a facility by its primary key
    def get_object(self, pk):
        try:
            return Facility.objects.get(pk=pk)
        except Facility.DoesNotExist:
            return None

    # Retrieve details of a specific facility
    def get(self, request, pk):
        facility = self.get_object(pk)
        if facility is None:
            return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)

        if facility.interaction_type == Facility.REGISTER:
            tenant = getattr(request.user, 'tenant', None)
            if tenant is None:
                return Response({'error': 'You need to be a tenant to access this facility'}, status=status.HTTP_403_FORBIDDEN)

            registration = FacilityRegistration.objects.filter(facility=facility, tenant=tenant).first()
            if registration:
                registration_serializer = FacilityRegistrationSerializer(registration)
                return Response({
                    'facility': self.serializer_class(facility).data,
                    'registration': registration_serializer.data
                })
            return Response({
                'facility': self.serializer_class(facility).data,
                'message': 'You need to register for this facility'
            })
        elif facility.interaction_type == Facility.CONTACT:
            return Response(self.serializer_class(facility).data)

        return Response(self.serializer_class(facility).data)

    # Update an existing facility
    def put(self, request, pk):
        facility = self.get_object(pk)
        if facility is None:
            return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(facility, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a facility
    def delete(self, request, pk):
        facility = self.get_object(pk)
        if facility is None:
            return Response({'error': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)

        facility.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterFacilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_name = request.data.get('tenant')  # Get tenant name directly
        facility_id = request.data.get('facility')

        try:
            tenant = Tenant.objects.get(name=tenant_name)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            facility = Facility.objects.get(id=facility_id)
        except Facility.DoesNotExist:
            return Response({'error': 'Facility not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the tenant is already registered for the facility
        registration, created = FacilityRegistration.objects.get_or_create(
            tenant=tenant,
            facility=facility
        )

        if not created:
            return Response({'error': 'You are already registered for this facility.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Registration successful.'}, status=status.HTTP_201_CREATED)


from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import FacilityRegistration  # Adjust the import according to your model
from .serializers import FacilityRegistrationSerializer  # Adjust as necessary

@api_view(['POST'])
def register_facility(request):
    tenant_name = request.data.get('tenant')
    facility_id = request.data.get('facility')

    # Check if a registration already exists
    existing_registration = FacilityRegistration.objects.filter(tenant__name=tenant_name, facility_id=facility_id).first()
    if existing_registration:
        return Response({'detail': 'You are already registered for this facility.'},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = FacilityRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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




# Notifi viewsfrom rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

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
    
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'}, status=status.HTTP_200_OK)





# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from datetime import datetime
import base64

def get_access_token():
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    json_response = response.json()
    return json_response['access_token']

@csrf_exempt
def lipa_na_mpesa(request):
    if request.method == 'POST':
        token = get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{settings.MPESA_BUSINESS_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        payload = {
            'BusinessShortCode': settings.MPESA_BUSINESS_SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': 1,  # Replace with the actual amount
            'PartyA': settings.MPESA_PHONE_NUMBER,
            'PartyB': settings.MPESA_BUSINESS_SHORTCODE,  # Typically same as BusinessShortCode
            'PhoneNumber': settings.MPESA_PHONE_NUMBER,
            'CallBackURL': 'https://yourdomain.com/mpesa/callback/',
            'AccountReference': 'AccountReference',
            'TransactionDesc': 'Payment for testing'
        }
        response = requests.post(api_url, json=payload, headers=headers)
        return JsonResponse(response.json())
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        # Process callback data here
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


# hostel/views.py

from django.shortcuts import HttpResponse
import matplotlib.pyplot as plt
from io import BytesIO

def generate_plot(request):
    # Example function to generate a plot
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    ax.set_title('Sample Plot')

    # Create a BytesIO buffer and save the plot to it
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')






from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Booking, Room
from .serializers import BookingSerializer
from django.utils import timezone

class BookRoomView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            room_id = serializer.validated_data['room_id']
            room = Room.objects.get(id=room_id)
            if room.is_booked:
                return Response({'error': 'Room is already booked'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(user=user)
            room.is_booked = True
            room.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get(self, request):
        user = request.user
        bookings = Booking.objects.filter(user=user)
        serializer = self.serializer_class(bookings, many=True)
        return Response(serializer.data)
    





    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Event
from .serializers import EventSerializer
import logging

logger = logging.getLogger(__name__)

class EventListCreateView(APIView):
    def get(self, request):
        try:
            events = Event.objects.all()
            serializer = EventSerializer(events, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = EventSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EventDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = EventSerializer

    def get_object(self, pk):
        """
        Helper method to get the object with the given pk
        """
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve an event by its ID
        """
        event = self.get_object(pk)
        if event is None:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(event)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update an event by its ID
        """
        event = self.get_object(pk)
        if event is None:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete an event by its ID
        """
        event = self.get_object(pk)
        if event is None:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import RVPDownload, Event, Tenant
from .serializers import RVPDownloadSerializer
import logging

logger = logging.getLogger(__name__)

class RVPDownloadCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_id = request.data.get('event')
        tenant_name = request.data.get('tenant_name')  # Ensure 'tenant_name' is used

        if not event_id:
            return Response({'error': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not tenant_name:
            return Response({'error': 'Tenant name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the event exists
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the tenant exists
        try:
            tenant = Tenant.objects.get(name=tenant_name)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the tenant has already downloaded the RVP for this event
        if RVPDownload.objects.filter(event=event, tenant=tenant).exists():
            return Response({'error': 'RVP for this event has already been downloaded by this tenant'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate RVP PDF with tenant's name
        if not event.rvp_file:
            event.rvp_file = event.create_default_rvp(tenant_name=tenant_name)
            event.save()

        # Prepare data for the serializer
        data = {
            'event': event_id,
            'tenant': tenant.id
        }

        serializer = RVPDownloadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def send_bypass_email(request):
    email = request.data.get('email')
    if email:
        # Logic to send bypass code via email
        return Response({"message": "Bypass code sent successfully."})
    else:
        return JsonResponse({"error": "Email not provided."}, status=400)
    
    from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tenant  # Make sure to import your Tenant model
import json

@csrf_exempt
def check_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if Tenant.objects.filter(email=email).exists():
            return JsonResponse({'exists': True}, status=200)
        else:
            return JsonResponse({'exists': False}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GenerateBypassCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Received request to generate bypass code for email: {email}")

        # Generate a 6-digit bypass code
        bypass_code = ''.join(random.choices(string.digits, k=6))
        print(f"Generated bypass code: {bypass_code}")

        # Store the bypass code in cache (with expiration)
        cache.set(f'bypass_code_{email}', bypass_code, timeout=60)  # Timeout in seconds
        print(f"Stored bypass code in cache with key: bypass_code_{email}")

        # Send bypass code to the email
        send_mail(
            'Your Bypass Code',
            f'Your bypass code is {bypass_code}. It will expire in 1 minute.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        print(f"Sent bypass code to email: {email}")

        return Response({'status': 'success', 'message': 'Bypass code sent successfully'}, status=status.HTTP_200_OK)

class VerifyBypassCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        bypass_code = request.data.get('bypass_code')

        if not email or not bypass_code:
            return Response({'detail': 'Email and bypass code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = cache.get(f'bypass_code_{email}')

        if stored_code is None:
            return Response({'detail': 'Bypass code not found or expired.'}, status=status.HTTP_400_BAD_REQUEST)

        if stored_code == bypass_code:
            cache.delete(f'bypass_code_{email}')
            return Response({'status': 'success', 'message': 'Bypass code verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid bypass code.'}, status=status.HTTP_400_BAD_REQUEST)
