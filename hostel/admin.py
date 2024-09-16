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
    RoomDescription,
    Event,
    RVPDownload,
    FacilityRegistration
)
from django.utils.html import format_html

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name", "address")

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hostel", "number", "room_type")
    list_filter = ("hostel", "room_type")
    search_fields = ("number",)

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone_number")
    search_fields = ("name", "email", "phone_number")

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "hostel")
    list_filter = ("position", "hostel")
    search_fields = ("name", "position")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "tenant", "check_in_date", "check_out_date")
    list_filter = ("room", "check_in_date", "check_out_date")
    search_fields = ("tenant__name", "room__number")

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("room", "description", "completed")
    list_filter = ("completed", "room")
    search_fields = ("description",)

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "hostel", "interaction_type", "contact_name", "contact_email", "contact_phone", "view_registered_tenants")
    list_filter = ("hostel", "interaction_type")
    search_fields = ("name", "contact_name", "contact_email", "contact_phone")

    def view_registered_tenants(self, obj):
        """View a list of tenants registered for the facility."""
        registrations = FacilityRegistration.objects.filter(facility=obj)
        if registrations.exists():
            return format_html(
                "<br>".join([f"{reg.tenant.name} - Token: {reg.registration_token}" for reg in registrations])
            )
        return "No registered tenants"
    view_registered_tenants.short_description = "Registered Tenants"

@admin.register(FacilityRegistration)
class FacilityRegistrationAdmin(admin.ModelAdmin):
    list_display = ("facility", "tenant", "registration_token")
    search_fields = ("tenant__name", "facility__name", "registration_token")
    list_filter = ("facility", "tenant")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("tenant", "amount", "date")
    list_filter = ("tenant", "date")
    search_fields = ("tenant__name", "amount")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "date")
    search_fields = ("message", "date")

@admin.register(RoomDescription)
class RoomDescriptionAdmin(admin.ModelAdmin):
    list_display = ("room", "price")
    list_filter = ("room",)
    search_fields = ("room__number", "price")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "likes", "view_rvp_link")
    search_fields = ("title", "description", "location")
    list_filter = ("date", "location")

    def view_rvp_link(self, obj):
        if obj.rvp_file:
            return format_html('<a href="{}" download>Download RVP</a>', obj.rvp_file.url)
        return "No RVP file"
    view_rvp_link.short_description = 'RVP File'

@admin.register(RVPDownload)
class RVPDownloadAdmin(admin.ModelAdmin):
    list_display = ("event", "tenant", "downloaded_at")
    list_filter = ("event", "tenant", "downloaded_at")
    search_fields = ("tenant__name", "event__title")
