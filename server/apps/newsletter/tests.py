from django.test import TestCase, Client
from django.urls import reverse
from .models import Subscriber
import unittest

class TestNewsletterViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.subscribe_url = reverse('newsletter:subscribe')
        self.unsubscribe_url = reverse('newsletter:unsubscribe', args=['test@example.com'])
        self.subscriber = Subscriber.objects.create(email='test@example.com', is_active=True)
    
    def test_subscribe_view_post_valid(self):
        response = self.client.post(self.subscribe_url, {'email': 'new@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Subscription successful')
        self.assertEqual(Subscriber.objects.count(), 2)
        self.assertTrue(Subscriber.objects.get(email='new@example.com').is_active)
    
    def test_subscribe_view_post_invalid(self):
        response = self.client.post(self.subscribe_url, {'email': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Email is required')
    
    def test_subscribe_view_post_duplicate(self):
        response = self.client.post(self.subscribe_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Email already subscribed')
    
    def test_unsubscribe_view_valid(self):
        response = self.client.get(reverse('newsletter:unsubscribe', args=['test@example.com']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsletter/unsubscribe_success.html')
        self.assertFalse(Subscriber.objects.get(email='test@example.com').is_active)
    
    def test_unsubscribe_view_invalid(self):
        response = self.client.get(reverse('newsletter:unsubscribe', args=['invalid@example.com']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsletter/unsubscribe_fail.html')

if __name__ == '__main__':
    unittest.main()