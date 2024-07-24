# views.py
from django.http import JsonResponse
from django.views import View
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



class RoomDescriptionDetailView(APIView):
    serializer_class = RoomDescriptionSerializer

    def get(self, request, room_number):
        try:
            room = Room.objects.get(number=room_number)
            room_description = RoomDescription.objects.get(room=room)
            serializer = self.serializer_class(room_description)
            return Response(serializer.data)
        except RoomDescription.DoesNotExist:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        room_description = self.get_object(pk)
        if room_description is None:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(room_description)
        return Response(serializer.data)

    def put(self, request, pk):
        room_description = self.get_object(pk)
        if room_description is None:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(room_description, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        room_description = self.get_object(pk)
        if room_description is None:
            return Response({'error': 'Room description not found'}, status=status.HTTP_404_NOT_FOUND)
        room_description.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




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
    permission_classes = [IsAuthenticated, IsAdminUser]
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


class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = BookingSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics
from .models import Booking
from .serializers import BookingSerializer

class BookingByRoomAndTenantView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        tenant_id = self.kwargs['tenant_id']
        return Booking.objects.filter(room_id=room_id, tenant_id=tenant_id)
    
    from datetime import datetime

def check_booking_overlap(room_id, tenant_id, check_in_date, check_out_date):
    bookings = Booking.objects.filter(
        room_id=room_id,
        tenant_id=tenant_id
    )

    for booking in bookings:
        if (check_in_date < booking.check_out_date and check_out_date > booking.check_in_date):
            return True  # Overlap found

    return False



class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
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




from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import base64

# Replace these values with your credentials
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
