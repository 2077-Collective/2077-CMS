import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from typing import Optional, Dict, Any
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def create_subscriber(self, email: str, is_active: bool = True) -> Dict[str, Any]:
        """
        Create a new subscriber in Beehiiv.
        """
        endpoint = f"{self.base_url}/publications/{self.publication_id}/subscriptions"
        
        data = {
            "email": email,
            "reactivate_existing": True,
            "send_welcome_email": True,
            "utm_source": "2077 Research",
            "status": "active" if is_active else "inactive"
        }
        
        try:
            logger.info(f"Creating Beehiiv subscriber: {email}")
            response = requests.post(endpoint, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for "invalid" status
            if data.get('data', {}).get('status') == 'invalid':
                logger.warning(f"Beehiiv API returned an invalid status for {email}")
                raise ValueError("Beehiiv API returned an invalid status. The email may need verification.")
            
            logger.info(f"Successfully created Beehiiv subscriber: {email}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Beehiiv subscriber {email}: {str(e)}")
            raise Exception(f"Failed to create Beehiiv subscriber: {str(e)}") from e
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def update_subscriber_status(self, email: str, is_active: bool) -> Dict[str, Any]:
        """
        Update subscriber status in Beehiiv.
        """
        endpoint = f"{self.base_url}/publications/{self.publication_id}/subscriptions/email:{email}"
        
        data = {
            "status": "active" if is_active else "inactive"
        }
        
        try:
            logger.info(f"Updating Beehiiv subscriber status: {email}")
            response = requests.patch(endpoint, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'id' not in data:
                logger.warning(f"Invalid response from Beehiiv API for {email}")
                raise ValueError("Invalid response from Beehiiv API")
            
            logger.info(f"Successfully updated Beehiiv subscriber status: {email}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update Beehiiv subscriber {email}: {str(e)}")
            raise Exception(f"Failed to update Beehiiv subscriber: {str(e)}") from e
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def delete_subscriber(self, email: str) -> bool:
        """
        Delete a subscriber from Beehiiv.
        """
        endpoint = f"{self.base_url}/publications/{self.publication_id}/subscriptions/email:{email}"
        
        try:
            logger.info(f"Deleting Beehiiv subscriber: {email}")
            response = requests.delete(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully deleted Beehiiv subscriber: {email}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete Beehiiv subscriber {email}: {str(e)}")
            raise Exception(f"Failed to delete Beehiiv subscriber: {str(e)}") from e