import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Booking)
def set_room_as_booked(sender, instance, created, **kwargs):
    if created:
        instance.room.is_booked = True
        instance.room.save()
        logger.info(f'Room {instance.room.number} set to booked.')

@receiver(post_delete, sender=Booking)
def set_room_as_unbooked(sender, instance, **kwargs):
    instance.room.is_booked = False
    instance.room.save()
    logger.info(f'Room {instance.room.number} set to available.')
    
# signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Booking, Room

@receiver(post_delete, sender=Booking)
def update_room_status_on_booking_delete(sender, instance, **kwargs):
    room = instance.room
    # Check if there are any remaining bookings for this room
    if not Booking.objects.filter(
        room=room,
        check_out_date__gt=timezone.now()
    ).exists():
        room.status = True  # Mark room as available
        room.save()
