# hostel/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet, RoomViewSet, TenantViewSet, StaffViewSet, 
    BookingViewSet, MaintenanceViewSet, FacilityViewSet, 
    PaymentViewSet, NotificationViewSet
)

router = DefaultRouter()
router.register(r'hostels', HostelViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'tenants', TenantViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'maintenances', MaintenanceViewSet)
router.register(r'facilities', FacilityViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
