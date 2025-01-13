import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from apps.newsletter.models import Subscriber

class Command(BaseCommand):
    help = 'Export subscribers to a CSV file'

    def handle(self, *args, **kwargs):
        try:
            export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
            os.makedirs(export_dir, exist_ok=True)

            csv_filename = os.path.join(export_dir, 'subscribers_export.csv')

            subscribers = Subscriber.objects.iterator()

            with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['email', 'is_active', 'subscribed_at']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, escapechar='\\', quoting=csv.QUOTE_ALL)

                writer.writeheader()

                for subscriber in subscribers:
                    safe_email = subscriber.email.replace('\n', '').replace('\r', '') if subscriber.email else ''
                    writer.writerow({
                        'email': safe_email,
                        'is_active': 'Yes' if subscriber.is_active else 'No',
                        'subscribed_at': timezone.localtime(subscriber.subscribed_at).isoformat() if subscriber.subscribed_at else ''
                    })

            self.stdout.write(self.style.SUCCESS(f'Successfully exported subscribers to {csv_filename}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error exporting subscribers: {str(e)}'))
            raise