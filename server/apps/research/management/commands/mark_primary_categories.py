from django.core.management.base import BaseCommand
from apps.research.models import Category

class Command(BaseCommand):
    help = 'Mark specific categories as primary (is_primary=True).'

    def handle(self, *args, **kwargs):
        # List of categories to mark as primary
        primary_categories = [
            "Layer 1",
            "Layer 2",
            "Interoperability",
            "DeFi",
            "DePIN",
            "Privacy",
        ]

        # Update the is_primary field for the specified categories
        updated_count = Category.objects.filter(name__in=primary_categories).update(is_primary=True)

        # Output the result
        self.stdout.write(
            self.style.SUCCESS(f'Successfully marked {updated_count} categories as primary.')
        )