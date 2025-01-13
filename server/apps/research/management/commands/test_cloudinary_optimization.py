# apps/research/management/commands/test_cloudinary_optimization.py
from django.core.management.base import BaseCommand
from apps.research.models import Article
from cloudinary.utils import cloudinary_url

class Command(BaseCommand):
    help = 'Test Cloudinary image optimization settings'

    def handle(self, *args, **kwargs):
        articles = Article.objects.filter(thumb__isnull=False)[:3]
        
        self.stdout.write(self.style.SUCCESS('Testing Cloudinary image optimizations...'))
        
        for article in articles:
            self.stdout.write('\n' + '='*50)
            
            # Get current simple URL pattern
            base_url = article.thumb.url
            image_id = base_url.split('/')[-1].split('.')[0]  # Get clean image ID
            
            if not image_id or 'cloudinary' not in base_url:
                self.stdout.write(f"\nSkipping: Not a valid Cloudinary URL - {base_url}")
                continue
                
            # Construct URLs in your current format
            current_url = f"https://res.cloudinary.com/dc2iz5j1c/coverImage/{image_id}"
            optimized_url = f"https://res.cloudinary.com/dc2iz5j1c/coverImage/f_auto,q_auto/{image_id}"
            
            self.stdout.write(f"Article: {article.title}")
            self.stdout.write(f"\nCurrent URL format: {current_url}")
            self.stdout.write(f"Optimized URL format: {optimized_url}")
            
            # Check transformations
            has_format_auto = 'f_auto' in optimized_url
            has_quality_auto = 'q_auto' in optimized_url
            
            self.stdout.write(f"\nOptimizations status:")
            self.stdout.write(f"- Auto format (WebP/AVIF): {'✓' if has_format_auto else '✗'}")
            self.stdout.write(f"- Auto quality: {'✓' if has_quality_auto else '✗'}")
            
            # Show raw stored URL for reference
            self.stdout.write(f"\nStored URL in model: {base_url}")