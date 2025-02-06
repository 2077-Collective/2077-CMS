from django.apps import AppConfig
import algoliasearch_django as algoliasearch
from algoliasearch_django.registration import RegistrationError

class ResearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.research'

    def ready(self):
        from .models.article import Article
        from .models.author import Author
        from .models.category import Category
        from .models.algolia_index import ArticleIndex, AuthorIndex, CategoryIndex

        try:
            algoliasearch.register(Article, ArticleIndex)
            algoliasearch.register(Author, AuthorIndex)
            algoliasearch.register(Category, CategoryIndex)
        except RegistrationError:
            pass