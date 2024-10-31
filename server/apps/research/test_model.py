import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Article, Author, Category

class TestArticleModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.author = Author.objects.create(user=self.user, full_name="Test Author", bio="Test Bio")
        self.category = Category.objects.create(name="Test Category")
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article content.",
            summary="Test summary",
            acknowledgement="Test acknowledgement",
            status="draft"
        )
        self.article.authors.add(self.author)
        self.article.categories.add(self.category)

    def test_calculate_min_read(self):
        self.assertEqual(self.article.calculate_min_read(), 1)
        self.article.content = " ".join(["word"] * 600)
        self.assertEqual(self.article.calculate_min_read(), 2)

    def test_default_values(self):
        self.assertEqual(self.article.status, 'draft')
        self.assertEqual(self.article.views, 0)
        self.assertFalse(self.article.is_sponsored)

class TestAuthorModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.author = Author.objects.create(user=self.user, bio="Test Bio", twitter_username="test_twitter", full_name="Test Author")

    def test_create_author(self):
        self.assertIsInstance(self.author, Author)
        self.assertEqual(self.author.user.username, "testuser")
        self.assertEqual(self.author.bio, "Test Bio")
        self.assertEqual(self.author.twitter_username, "test_twitter")
        self.assertEqual(self.author.full_name, "Test Author")

if __name__ == '__main__':
    unittest.main()