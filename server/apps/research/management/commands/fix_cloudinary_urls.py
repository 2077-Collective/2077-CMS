import cloudinary.uploader
from django.core.management.base import BaseCommand
from apps.research.models import Article
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix broken Cloudinary URLs by re-uploading to images folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        # Find articles with broken Cloudinary URLs
        articles = Article.objects.filter(thumb__contains='res.cloudinary.com/dc2iz5j1c/images/')
        total = articles.count()
        
        self.stdout.write(f"Found {total} articles with broken Cloudinary URLs")

        for index, article in enumerate(articles, 1):
            self.stdout.write(f"Processing article {index}/{total}: {article.title}")
            
            try:
                current_thumb = str(article.thumb)
                filename = current_thumb.split('/')[-1]
                
                if not dry_run:
                    # Download from CMS
                    cms_url = f"https://cms.2077.xyz/media/images/{filename}"
                    self.stdout.write(f"Downloading from: {cms_url}")
                    
                    response = requests.get(cms_url)
                    if response.status_code == 200:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            response.content,
                            folder='images',
                            resource_type='auto'
                        )
                        
                        # Update article
                        article.thumb = result['public_id']
                        article.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Fixed URL for: {article.title}\n"
                                f"Old: {current_thumb}\n"
                                f"New: {result['public_id']}"
                            )
                        )
                    else:
                        self.stderr.write(f"Failed to download image from {cms_url}")
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"DRY RUN: Would fix: {article.title}\n"
                            f"Current URL: {current_thumb}"
                        )
                    )
                    
            except Exception as e:
                logger.error(f"Error processing article {article.id}: {str(e)}")
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to process article {article.title}: {str(e)}"
                    )
                )

        self.stdout.write(self.style.SUCCESS('URL migration completed'))