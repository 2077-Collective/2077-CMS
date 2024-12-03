# apps/research/models.py

from .category import Category
from .author import Author
from .article import Article, ArticleSlugHistory

__all__ = ['Category', 'Author', 'Article', 'ArticleSlugHistory']
