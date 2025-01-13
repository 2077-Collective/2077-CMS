import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from apps.newsletter.models import Subscriber  # Correct import path

class Command(BaseCommand):
    help = 'Export subscribers to a CSV file'

    def handle(self, *args, **kwargs):
        try:
            # Define the export directory and ensure it exists
            export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
            os.makedirs(export_dir, exist_ok=True)

            # Define the full path for the CSV file
            csv_filename = os.path.join(export_dir, 'subscribers_export.csv')

            # Use iterator() for memory efficiency with large datasets
            subscribers = Subscriber.objects.iterator()

            # Open the CSV file for writing
            with open(csv_filename, mode='w', newline='') as csv_file:
                fieldnames = ['email', 'is_active', 'subscribed_at']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                # Write the header row
                writer.writeheader()

                # Write each subscriber's data to the CSV file
                for subscriber in subscribers:
                    writer.writerow({
                        'email': subscriber.email or '',
                        'is_active': 'Yes' if subscriber.is_active else 'No',
                        'subscribed_at': timezone.localtime(subscriber.subscribed_at).isoformat() if subscriber.subscribed_at else ''
                    })

            # Success message
            self.stdout.write(self.style.SUCCESS(f'Successfully exported subscribers to {csv_filename}'))

        except Exception as e:
            # Handle errors and log them
            self.stderr.write(self.style.ERROR(f'Error exporting subscribers: {str(e)}'))
            raise