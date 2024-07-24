# models.py

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

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="rooms")
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES, default="bedsitter")
    image = models.ImageField(upload_to="room_images/", null=True, blank=True)

    def __str__(self):
        return f"Room {self.number} ({self.get_room_type_display()}) in {self.hostel.name}"
    


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
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=12)

    def __str__(self):
        return self.name


class Staff(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="staff")
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, ({self.position})"



from django.db import models

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="bookings")
    check_in_date = models.DateField()
    check_out_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tenant'], name='unique_tenant_booking')
        ]

    def __str__(self):
        return f"{self.tenant.name} booking for Room {self.room.number}"




class Maintenance(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="maintenance")
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'Maintenance for Room {self.room.number} - {"Completed" if self.completed else "Pending"}'

class Facility(models.Model):
    hostel = models.ForeignKey(
        Hostel, on_delete=models.CASCADE, related_name="facilities"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="facility_images/", null=True, blank=True)

    def __str__(self):
        return f"{self.name} at {self.hostel.name}"

class Payment(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} by {self.tenant.name} on {self.date}"

class Notification(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.tenant.name if self.tenant else "all"}: {self.message[:20]}...'