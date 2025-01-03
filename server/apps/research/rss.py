from django.contrib.syndication.views import Feed
from .models import Article
from django.conf import settings

class LatestArticlesFeed(Feed):
    title = "Latest Research Articles"
    description = "Stay updated with the latest research articles."

    def __call__(self, request, *args, **kwargs):
        # Store the request object for use in other methods
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def link(self):
        # Dynamically generate the link for the RSS feed using the request object
        return self.request.build_absolute_uri('/research/rss/')

    def items(self):
        # Return most recent published articles up to configured limit
        limit = getattr(settings, 'RSS_FEED_LIMIT', 10)
        return Article.objects.filter(status='ready').order_by('-scheduled_publish_time')[:limit]

    def item_title(self, item):
        # Return the article title
        return item.title

    def item_description(self, item):
        # Return the article summary
        return item.summary

    def item_link(self, item):
        # Manually construct the URL to avoid duplicating the '/api/' prefix
        return f"{self.request.build_absolute_uri('/')}api/articles/{item.slug}/"

    def item_pubdate(self, item):
        # Return the article's scheduled publish time
        return item.scheduled_publish_time

    def item_author_name(self, item):
        # Return the author's name(s) as a comma-separated string
        return ", ".join(
            [author.full_name or author.user.get_full_name() or author.user.username for author in item.authors.all()]
        )

    def item_categories(self, item):
        # Return the article's categories as a list
        return [category.name for category in item.categories.all()]