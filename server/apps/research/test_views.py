import unittest
from rest_framework.test import APIRequestFactory
from .views import ArticleViewSet

class TestArticleViewSet(unittest.TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_serializer_context(self):
        request = self.factory.get('/')
        view = ArticleViewSet()
        view.request = request
        context = view.get_serializer_context()
        self.assertIn('request', context)
        self.assertEqual(context['request'], request)

if __name__ == '__main__':
    unittest.main()