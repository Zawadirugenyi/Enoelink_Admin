from django.contrib import admin
from django.urls import path
from .views import (
    HostelListView, HostelDetailView, RoomListView, RoomDetailView, 
    TenantListView, TenantDetailView, StaffListView, StaffDetailView,
    BookingListView, BookingDetailView, MaintenanceListView, MaintenanceDetailView, 
    FacilityListView, FacilityDetailView, PaymentListView, PaymentDetailView, 
    NotificationListView, NotificationDetailView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Hostels
    path('api/hostels/', HostelListView.as_view(), name='hostel-list'),
    path('api/hostels/<int:pk>/', HostelDetailView.as_view(), name='hostel-detail'),

    # Rooms
    path('api/rooms/', RoomListView.as_view(), name='room-list'),
    path('api/rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),

    # Tenants
    path('api/tenants/', TenantListView.as_view(), name='tenant-list'),
    path('api/tenants/<int:pk>/', TenantDetailView.as_view(), name='tenant-detail'),

    # Staff
    path('api/staff/', StaffListView.as_view(), name='staff-list'),
    path('api/staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),

    # Bookings
    path('api/bookings/', BookingListView.as_view(), name='booking-list'),
    path('api/bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),

    # Maintenance
    path('api/maintenance/', MaintenanceListView.as_view(), name='maintenance-list'),
    path('api/maintenance/<int:pk>/', MaintenanceDetailView.as_view(), name='maintenance-detail'),

    # Facilities
    path('api/facilities/', FacilityListView.as_view(), name='facility-list'),
    path('api/facilities/<int:pk>/', FacilityDetailView.as_view(), name='facility-detail'),

    # Payments
    path('api/payments/', PaymentListView.as_view(), name='payment-list'),
    path('api/payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),

    # Notifications
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('api/notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hostel.urls')),  # Adjust according to your app name
]
