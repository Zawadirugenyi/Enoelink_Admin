# your_app/management/commands/populate_facilities.py
from django.core.management.base import BaseCommand
from hostel.models import Facility, Hostel

class Command(BaseCommand):
    help = 'Populate the database with initial facility data'

    def handle(self, *args, **kwargs):
        hostel_instance = Hostel.objects.first()  # Adjust as needed

        # Creating facility instances with updated interaction types
        facilities = [
            {"name": "Swimming Pool", "description": "Olympic size pool with heated water.", "interaction_type": Facility.REGISTER},
            {"name": "Parking", "description": "Secure parking lot with 24/7 surveillance.", "interaction_type": Facility.REGISTER},
            {"name": "Gym", "description": "Fully equipped gym with personal trainers.", "interaction_type": Facility.REGISTER},
            {"name": "Washing/Bussing", "description": "On-demand laundry and dry cleaning service.", "interaction_type": Facility.CONTACT},
            {"name": "Driver", "description": "Professional driver service for personal transport.", "interaction_type": Facility.CONTACT},
            {"name": "Local Market", "description": "A market providing fresh groceries and essentials.", "interaction_type": Facility.CONTACT},
            {"name": "Online Market", "description": "Online platform for purchasing goods with delivery options.", "interaction_type": Facility.REGISTER},
            {"name": "Gaz Delivery", "description": "Delivery service for gas.", "interaction_type": Facility.CONTACT},
            {"name": "Water Delivery", "description": "Delivery service for water.", "interaction_type": Facility.CONTACT},
        ]

        for facility_data in facilities:
            Facility.objects.create(
                hostel=hostel_instance,
                name=facility_data["name"],
                description=facility_data["description"],
                interaction_type=facility_data["interaction_type"]
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated facilities'))
