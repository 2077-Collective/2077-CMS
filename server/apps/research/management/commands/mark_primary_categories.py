from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import DatabaseError
from apps.research.models import Category

class Command(BaseCommand):
    help = 'Mark specific categories as primary (is_primary=True).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **kwargs):
        dry_run = kwargs.get('dry_run', False)

        # List of categories to mark as primary
        primary_categories = [
            "Layer 1",
            "Layer 2",
            "Interoperability",
            "DeFi",
            "DePIN",
            "Privacy",
        ]

        # Validate categories exist
        missing_categories = set(primary_categories) - set(
            Category.objects.filter(name__in=primary_categories).values_list('name', flat=True)
        )
        if missing_categories:
            self.stdout.write(
                self.style.WARNING(f'Categories not found: {", ".join(missing_categories)}')
            )

        try:
            with transaction.atomic():
                # First unmark all primary categories
                if not dry_run:
                    Category.objects.filter(is_primary=True).update(is_primary=False)

                # Update the is_primary field for the specified categories
                categories_to_update = Category.objects.filter(name__in=primary_categories)
                if dry_run:
                    self.stdout.write(
                        f'Would mark these categories as primary: {", ".join(categories_to_update.values_list("name", flat=True))}'
                    )
                else:
                    updated_count = categories_to_update.update(is_primary=True)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully marked {updated_count} categories as primary.')
                    )
        except DatabaseError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to update categories: {str(e)}')
            )
            return