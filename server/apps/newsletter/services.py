import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from typing import Optional, Dict, Any

class BeehiivService:
    def __init__(self):
        self.api_key = getattr(settings, 'BEEHIIV_API_KEY', None)
        self.publication_id = getattr(settings, 'BEEHIIV_PUBLICATION_ID', None)
        
        if not self.api_key or not self.publication_id:
            raise ImproperlyConfigured(
                "BEEHIIV_API_KEY and BEEHIIV_PUBLICATION_ID must be set in your environment"
            )
            
        self.base_url = "https://api.beehiiv.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_subscriber(self, email: str, is_active: bool = True) -> Dict[str, Any]:
        """
        Create a new subscriber in Beehiiv
        """
        endpoint = f"{self.base_url}/publications/{self.publication_id}/subscriptions"
        
        data = {
            "email": email,
            "reactivate_existing": True,
            "send_welcome_email": True,
            "utm_source": "django_website",
            "status": "active" if is_active else "inactive"
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'id' not in data:
                raise ValueError("Invalid response from Beehiiv API")
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create Beehiiv subscriber: {str(e)}") from e
    
    def update_subscriber_status(self, email: str, is_active: bool) -> Dict[str, Any]:
        """
        Update subscriber status in Beehiiv
        """
        endpoint = f"{self.base_url}/publications/{self.publication_id}/subscriptions/email:{email}"
        
        data = {
            "status": "active" if is_active else "inactive"
        }
        
        try:
            response = requests.patch(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to update Beehiiv subscriber: {str(e)}")
    
    def delete_subscriber(self, email: str) -> bool:
        """
        Delete a subscriber from Beehiiv
        """
        endpoint = f"{self.base_url}/publications/{self.publication_id}/subscriptions/email:{email}"
        
        try:
            response = requests.delete(endpoint, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to delete Beehiiv subscriber: {str(e)}")