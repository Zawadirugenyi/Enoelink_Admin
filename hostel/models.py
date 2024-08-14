from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

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
    position = models.CharField(max_length=255)

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
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()

    def save(self, *args, **kwargs):
        # Custom save logic
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Custom delete logic if needed
        super().delete(*args, **kwargs)


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


class Facility(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="facilities")
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="facility_images/", null=True, blank=True)

    def __str__(self):
        return f"{self.name} at {self.hostel.name}"


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