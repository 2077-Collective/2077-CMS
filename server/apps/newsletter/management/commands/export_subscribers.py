import csv
from django.core.management.base import BaseCommand
from apps.newsletter.models import Subscriber  # Correct import path

class Command(BaseCommand):
    help = 'Export subscribers to a CSV file'

    def handle(self, *args, **kwargs):
        subscribers = Subscriber.objects.all()
        csv_filename = 'subscribers_export.csv'

        with open(csv_filename, mode='w', newline='') as csv_file:
            fieldnames = ['email', 'is_active', 'subscribed_at']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for subscriber in subscribers:
                writer.writerow({
                    'email': subscriber.email,
                    'is_active': subscriber.is_active,
                    'subscribed_at': subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M:%S')
                })

        self.stdout.write(self.style.SUCCESS(f'Successfully exported subscribers to {csv_filename}'))