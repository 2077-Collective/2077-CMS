from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.xmlutils import SimplerXMLGenerator
from .models import Article
from django.conf import settings
import io

class PrettyXMLGenerator(SimplerXMLGenerator):
    def __init__(self, out=None, encoding='utf-8'):
        super().__init__(out, encoding)
        self._indent = 0
        self._indent_string = '  '

    def startElement(self, name, attrs):
        self._write('\n' + self._indent_string * self._indent)
        self._indent += 1
        super().startElement(name, attrs)

    def endElement(self, name):
        self._indent -= 1
        if self._pending_start_element:
            self._write('>')
            self._pending_start_element = False
        else:
            self._write('\n' + self._indent_string * self._indent)
        super().endElement(name)

    def characters(self, content):
        if content and content.strip():
            super().characters(content)

class PrettyRssFeed(Rss201rev2Feed):
    def write(self, outfile, encoding):
        handler = PrettyXMLGenerator(outfile, encoding)
        handler.startDocument()
        
        handler.startElement("rss", self.rss_attributes())
        handler.startElement("channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        handler.endElement("channel")
        handler.endElement("rss")

    def rss_attributes(self):
        attrs = super().root_attributes()
        attrs['version'] = "2.0"
        attrs['xmlns:snf'] = 'http://www.smartnews.be/snf'
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        attrs['xmlns:g'] = 'http://base.google.com/ns/1.0'
        attrs['xmlns:dc'] = 'http://purl.org/dc/elements/1.1/'
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        
        handler.startElement('guid', {})
        handler.characters(item['link'])
        handler.endElement('guid')
        
        if item.get('author_name'):
            handler.startElement('dc:creator', {})
            handler.characters(item['author_name'])
            handler.endElement('dc:creator')
            
        if item.get('image'):
            handler.startElement('g:image_link', {})
            handler.characters(item['image'])
            handler.endElement('g:image_link')

class LatestArticlesFeed(Feed):
    feed_type = PrettyRssFeed
    title = "Latest Research Articles"
    description = "Stay updated with the latest research articles."
    language = "en-us"
    
    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def link(self):
        return self.request.build_absolute_uri('/research/rss/')

    def feed_extra_kwargs(self, obj):
        return {
            'docs': 'http://blogs.law.harvard.edu/tech/rss'
        }

    def items(self):
        limit = getattr(settings, 'RSS_FEED_LIMIT', 20)
        return Article.objects.filter(status='ready').order_by('-scheduled_publish_time')[:limit]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        description = []
        if hasattr(item, 'featured_image') and item.featured_image:
            img_url = item.featured_image.url
            description.append(f'<img src="{img_url}">')
        
        description.append(item.summary)
        description.append(f'<a href="{self.item_link(item)}"><strong>READ MORE...</strong></a>')
        
        return '\n'.join(description)

    def item_link(self, item):
        return f"{self.request.build_absolute_uri('/')}api/articles/{item.slug}/"

    def item_pubdate(self, item):
        return item.scheduled_publish_time

    def item_author_name(self, item):
        try:
            return ", ".join(
                [author.full_name or author.user.get_full_name() or author.user.username 
                for author in item.authors.all()]
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching authors for article {item.id}: {e}")
            return "Unknown Author"

    def item_categories(self, item):
        try:
            return [category.name for category in item.categories.all()]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching categories for article {item.id}: {e}")
            return []

    def item_extra_kwargs(self, item):
        extra = {}
        if hasattr(item, 'featured_image') and item.featured_image:
            extra['image'] = item.featured_image.url
        return extra