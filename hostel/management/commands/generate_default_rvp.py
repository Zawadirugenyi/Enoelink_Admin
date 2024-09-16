from django.core.management.base import BaseCommand
from hostel.models import Event
from hostel.utils import create_default_rvp  # Import from the utils module

class Command(BaseCommand):
    help = 'Generate default RVP files for events'

    def handle(self, *args, **kwargs):
        events = Event.objects.filter(rvp_file__isnull=True)
        for event in events:
            # Generate a realistic RVP file with event details
            rvp_file_path = create_default_rvp(event.title, event.date)
            # Assign the file path to the event
            event.rvp_file = rvp_file_path
            event.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully generated default RVP files.'))
