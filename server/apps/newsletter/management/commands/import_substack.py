import csv
from django.core.management.base import BaseCommand
from apps.newsletter.models import Subscriber
from django.utils import timezone
from django.db import IntegrityError
import pytz


class Command(BaseCommand):
    help = "Import existing Substack subscribers"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to Substack CSV file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        imported = 0
        skipped = 0
        errors = 0

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                email = row.get("email", "").strip().lower()
                if email:
                    try:
                        created_at = timezone.datetime.strptime(
                            row["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        # Make it timezone aware
                        created_at = timezone.make_aware(created_at)

                        subscriber, created = Subscriber.objects.get_or_create(
                            email=email,
                            defaults={"is_active": True, "subscribed_at": created_at},
                        )

                        if created:
                            imported += 1
                            self.stdout.write(f"Imported: {email}")
                        else:
                            skipped += 1
                            self.stdout.write(f"Skipped (already exists): {email}")

                    except Exception as e:
                        errors += 1
                        self.stdout.write(
                            self.style.WARNING(f"Error processing {email}: {str(e)}")
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete: {imported} imported, {skipped} errors: {errors}"
            )
        )
