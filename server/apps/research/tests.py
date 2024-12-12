from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from .models import Article, RelatedArticle
from .models import Article
from datetime import datetime, timedelta
from django.utils import timezone

class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_article_creation(self):
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            summary='This is a summary.',
            author=self.user,
            status='ready'
        )
        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(article.content, 'This is a test article.')
        self.assertEqual(article.summary, 'This is a summary.')
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.status, 'ready')
        self.assertEqual(article.views, 0)

    def test_slug_generation(self):
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            author=self.user,
            status='ready'
        )
        self.assertEqual(article.slug, 'test-article')

        article2 = Article.objects.create(
            title='Test Article',
            content='This is another test article.',
            author=self.user,
            status='ready'
        )
        self.assertEqual(article2.slug, 'test-article-1')

    def test_custom_manager(self):
        Article.objects.create(
            title='Draft Article',
            content='This is a draft article.',
            author=self.user,
            status='draft'
        )
        ready_article = Article.objects.create(
            title='Ready Article',
            content='This is a ready article.',
            author=self.user,
            status='ready'
        )
        articles = Article.postobjects.all()
        self.assertEqual(articles.count(), 1)
        self.assertEqual(articles.first(), ready_article)

    def test_ordering(self):
        now = timezone.now()
        article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=self.user,
            created_at=now - timedelta(days=1),
            status='ready'
        )
        article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            author=self.user,
            created_at=now,
            status='ready'
        )
        articles = Article.objects.all()
        self.assertEqual(articles.first(), article2)
        self.assertEqual(articles.last(), article1)

    def test_default_views(self):
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            author=self.user,
            status='ready'
        )
        self.assertEqual(article.views, 0)

    def test_increment_views(self):
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            author=self.user,
            status='ready'
        )
        article.views += 1
        article.save()
        article.refresh_from_db()
        self.assertEqual(article.views, 1)
        
class RelatedArticleModelTest(TestCase):
    def setUp(self):
        # Create test articles without author field
        self.article1 = Article.objects.create(
            title='Test Article 1',
            content='Content 1',
            status='ready'
        )
        self.article2 = Article.objects.create(
            title='Test Article 2',
            content='Content 2',
            status='ready'
        )
        self.article3 = Article.objects.create(
            title='Test Article 3',
            content='Content 3',
            status='ready'
        )
        self.article4 = Article.objects.create(
            title='Test Article 4',
            content='Content 4',
            status='ready'
        )

    def test_prevent_self_reference(self):
        """Test that an article cannot be related to itself"""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RelatedArticle.objects.create(
                    from_article=self.article1,
                    to_article=self.article1
                )

    def test_prevent_circular_reference(self):
        """Test that circular references are prevented"""
        # Create first relationship
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article2
        )
        
        # Attempt to create circular reference
        with self.assertRaises(ValidationError):
            RelatedArticle.objects.create(
                from_article=self.article2,
                to_article=self.article1
            )

    def test_maximum_related_articles(self):
        """Test that maximum of 3 related articles is enforced"""
        # Create three related articles
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article2
        )
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article3
        )
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article4
        )

        # Create fifth article and attempt to add it as fourth relation
        article5 = Article.objects.create(
            title='Test Article 5',
            content='Content 5',
            status='ready'
        )

        # Attempt to add fourth related article
        with self.assertRaises(ValidationError):
            RelatedArticle.objects.create(
                from_article=self.article1,
                to_article=article5
            )

    def test_unique_relationships(self):
        """Test that duplicate relationships are prevented"""
        # Create first relationship
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article2
        )

        # Attempt to create duplicate relationship
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RelatedArticle.objects.create(
                    from_article=self.article1,
                    to_article=self.article2
                )

    def test_get_related_articles(self):
        """Test the get_related_articles method"""
        # Create related articles
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article2
        )
        RelatedArticle.objects.create(
            from_article=self.article1,
            to_article=self.article3
        )

        related = self.article1.get_related_articles()
        self.assertEqual(related.count(), 2)
        self.assertIn(self.article2, related)
        self.assertIn(self.article3, related)