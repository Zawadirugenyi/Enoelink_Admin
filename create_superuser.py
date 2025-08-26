# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_hostel_pro.settings")
django.setup()

from users.models import User

EMAIL = "admin@gmail.com"   # Change to your desired admin email
PASSWORD = "Admin12345@"       # Change to your desired password
FIRST_NAME = "Admin"
LAST_NAME = "User"
PHONE = 1234567890            # Use a valid phone number

if not User.objects.filter(email=EMAIL).exists():
    User.objects.create_superuser(
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        email=EMAIL,
        phone_number=PHONE,
        password=PASSWORD
    )
    print("Superuser created!")
else:
    print("Superuser already exists.")
