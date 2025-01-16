from django.core.management.base import BaseCommand
from newsletter.models import Subscriber
from newsletter.services import BeehiivService

class Command(BaseCommand):
    help = 'Syncs all existing subscribers to Beehiiv'

    def handle(self, *args, **options):
        beehiiv = BeehiivService()
        subscribers = Subscriber.objects.all()
        success_count = 0
        error_count = 0

        self.stdout.write('Starting subscriber sync...')

        for subscriber in subscribers:
            try:
                beehiiv.create_subscriber(subscriber.email, subscriber.is_active)
                success_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully synced subscriber: {subscriber.email}'
                ))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f'Failed to sync subscriber {subscriber.email}: {str(e)}'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Sync completed. Success: {success_count}, Errors: {error_count}'
        ))