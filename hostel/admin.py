from django.contrib import admin
from .models import (
    Hostel,
    Room,
    Tenant,
    Staff,
    Booking,
    Maintenance,
    Facility,
    Payment,
    Notification,
)


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ("name", "address")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hostel", "number", "room_type")
    list_filter = ("hostel", "room_type")


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "hostel")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "tenant", "check_in_date", "check_out_date")


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("room", "description", "completed")
    list_filter = ("completed",)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "hostel")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("tenant", "amount", "date")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "date")
    search_fields = ("message",)
