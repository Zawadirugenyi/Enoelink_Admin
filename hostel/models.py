from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


from django.db import models



class Hostel(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    image = models.ImageField(upload_to="hostel_images/", null=True, blank=True)
    
    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_TYPES = (
        ("bedsitter", "Bedsitter"),
        ("one_bedroom", "One Bedroom"),
        ("two_bedrooms", "Two Bedrooms"),
        ("three_bedrooms", "Three Bedrooms"),
    )

    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE, related_name="rooms")
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES, default="bedsitter")
    image = models.ImageField(upload_to="room_images/", null=True, blank=True)
    status = models.BooleanField(default=True)  # True means available, False means occupied

    # Reference to Tenant
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)

    def __str__(self):
        return f"Room {self.number} ({self.get_room_type_display()}) in {self.hostel.name}"


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    major = models.CharField(max_length=255)
    admin_number = models.CharField(max_length=255)
    gender = models.CharField(max_length=255, default='Not specified')
    nationality = models.CharField(max_length=255, default='Unknown')
    passport = models.CharField(max_length=20, default='Unknown')
    phone_number = models.CharField(max_length=12)
    email = models.EmailField(unique=True)
    passport_photo = models.ImageField(upload_to="tenant_image/", null=True, blank=True)
    parent = models.CharField(max_length=20, default='Unknown')
    relationship = models.CharField(max_length=255)
    guardian_contact = models.CharField(max_length=12)

    def __str__(self):
        return self.name


class RoomDescription(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="description")
    sitting_room_image = models.ImageField(upload_to='room_description_images/', null=True, blank=True)
    bedroom_image = models.ImageField(upload_to='room_description_images/', null=True, blank=True)
    kitchen_image = models.ImageField(upload_to='room_description_images/', null=True, blank=True)
    bathroom_image = models.ImageField(upload_to='room_description_images/', null=True, blank=True)
    description = models.TextField(max_length=2000)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Description for Room {self.room.number}'


class Staff(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="staff")
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, ({self.position})"


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()

    def save(self, *args, **kwargs):
        # Custom save logic
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Custom delete logic if needed
        super().delete(*args, **kwargs)

    @classmethod
    def get_room_by_tenant_and_booking(cls, tenant_id, booking_id):
        try:
            booking = cls.objects.get(id=booking_id, tenant_id=tenant_id)
            return booking.room
        except cls.DoesNotExist:
            return None



class Maintenance(models.Model):
    REQUISITION_TYPES = [
        ('maintenance', 'Maintenance'),
        ('facility', 'Facility'),
        ('other', 'Other'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="maintenance")
    room_number = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=REQUISITION_TYPES, default='maintenance')
    otherType = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.room_number = self.room.number  # Ensure room_number is always in sync with room
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_type_display()} for Room {self.room.number} - {"Completed" if self.completed else "Pending"}'
from django.db import models
from django.utils.crypto import get_random_string

class Facility(models.Model):
    """Represents a facility associated with a hostel."""
    
    REGISTER = 'register'
    CONTACT = 'contact'

    INTERACTION_CHOICES = [
        (REGISTER, 'Register'),
        (CONTACT, 'Contact'),
    ]

    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE, related_name="facilities")
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="facility_images/", null=True, blank=True)
    contact_name = models.CharField(max_length=255, null=True, blank=True)  
    contact_email = models.EmailField(max_length=255, null=True, blank=True)  
    contact_phone = models.CharField(max_length=20, null=True, blank=True)  
    interaction_type = models.CharField(
        max_length=10,
        choices=INTERACTION_CHOICES,
        default=CONTACT,
    )

    def __str__(self):
        return f"{self.name} at {self.hostel.name if self.hostel else 'Unknown Hostel'}"


class FacilityRegistration(models.Model):
    """Handles tenant registrations for a facility."""
    
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
    facility = models.ForeignKey('Facility', on_delete=models.CASCADE)
    registration_token = models.CharField(max_length=12, blank=True)

    class Meta:
        unique_together = (('tenant', 'facility'),)

    def generate_token(self):
        """Generates a random registration token."""
        self.registration_token = get_random_string(12)
        self.save()

    def save(self, *args, **kwargs):
        """Overrides the save method to ensure a registration token is generated if not present."""
        if not self.registration_token:
            self.generate_token()
        super().save(*args, **kwargs) 

        
class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} by {self.tenant.name} on {self.date}"


from django.db import models

class Notification(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.tenant.name if self.tenant else "all"}: {self.message[:20]}...'

    @property
    def tenant_name(self):
        return self.tenant.name if self.tenant else "No tenant"



class Request(models.Model):
    user = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='requests')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Request by {self.user.name} on {self.created_at}'

from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from django.core.files.base import ContentFile
from urllib.parse import quote
import random

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)
    rvp_file = models.FileField(upload_to="rvp_files/", null=True, blank=True)
    likes = models.PositiveIntegerField(default=0)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='events', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Only create an RVP file if none exists
        if not self.rvp_file:
            # Check if tenant_name is available
            tenant_name = self.tenant.name if self.tenant else "Unknown Tenant"
            self.rvp_file = self.create_default_rvp(tenant_name=tenant_name)
        super().save(*args, **kwargs)

    def create_default_rvp(self, tenant_name):
        # Encode the tenant name
        encoded_tenant_name = quote(tenant_name)

        # Create a PDF with event details
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        content = []

        # Teal Color Scheme
        teal = colors.HexColor('#008080')
        light_teal = colors.HexColor('#20B2AA')
        dark_teal = colors.HexColor('#004d40')
        light_background = colors.HexColor('#e0f2f1')
        teal_text = colors.HexColor('#004d40')

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.textColor = teal
        body_style = styles['BodyText']
        body_style.textColor = teal_text
        conclusion_style = ParagraphStyle(
            name='ConclusionStyle',
            fontSize=10,
            alignment=1,
            spaceAfter=20,
            textColor=teal_text
        )

        # Title
        content.append(Paragraph(f"Event Ticket: {self.title}", title_style))

        # Serial Number
        serial_number = f"Serial Number: {random.randint(100000, 999999)}"
        content.append(Paragraph(serial_number, body_style))

        # Event and Tenant Details
        details = [
           # Use tenant_name directly
            ["Event Title:", self.title],
            ["Date:", self.date.strftime("%A, %B %d, %Y")],
            ["Location:", self.location],
            ["Description:", Paragraph(self.description, body_style)],
        ]

        # Table with adjusted column width for the description
        table = Table(details, colWidths=[120, 440])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), dark_teal),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), light_background),
            ('GRID', (0, 0), (-1, -1), 1, dark_teal),
        ]))

        content.append(table)

        # Conclusion
        content.append(Paragraph("Thank you for joining us. We look forward to seeing you at the event!", conclusion_style))

        # Build PDF
        doc.build(content)
        buffer.seek(0)

        # Create a unique filename for the PDF
        file_name = f"{self.title.replace(' ', '_')}_{random.randint(1000, 9999)}.pdf"
        return ContentFile(buffer.read(), file_name)

    def __str__(self):
        return self.title

class RVPDownload(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else 'No tenant'
        event_title = self.event.title if self.event else 'Unknown event'
        return f"{tenant_name} downloaded {event_title} on {self.downloaded_at}"
