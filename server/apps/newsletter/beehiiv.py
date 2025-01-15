import requests
from django.conf import settings
from typing import Dict, Any

class BeehiivClient:
    BASE_URL = "https://api.beehiiv.com/v2"
    
    def __init__(self):
        self.api_key = settings.BEEHIIV_API_KEY
        self.publication_id = settings.BEEHIIV_PUBLICATION_ID
        
    def create_subscriber(self, email: str) -> Dict[str, Any]:
        """
        Create a new subscriber in Beehiiv
        
        Args:
            email (str): Email address of the subscriber
            
        Returns:
            Dict[str, Any]: Response from Beehiiv API
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        endpoint = f"{self.BASE_URL}/publications/{self.publication_id}/subscriptions"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "email": email,
            "reactivate_existing": True,
            "send_welcome_email": True,
            "utm_source": "website"
        }
        
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    def bulk_create_subscribers(self, emails: list[str]) -> Dict[str, Any]:
        """
        Bulk create subscribers in Beehiiv
        
        Args:
            emails (list[str]): List of email addresses
            
        Returns:
            Dict[str, Any]: Response from Beehiiv API
        """
        endpoint = f"{self.BASE_URL}/publications/{self.publication_id}/subscriptions/bulk"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "subscribers": [{"email": email} for email in emails],
            "reactivate_existing": True,
            "send_welcome_email": True,
            "utm_source": "website"
        }
        
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    def get_subscriber(self, email: str) -> Dict[str, Any]:
        """
        Get subscriber details from Beehiiv
        
        Args:
            email (str): Email address of the subscriber
            
        Returns:
            Dict[str, Any]: Response from Beehiiv API
        """
        endpoint = f"{self.BASE_URL}/publications/{self.publication_id}/subscriptions/email/{email}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        return response.json()