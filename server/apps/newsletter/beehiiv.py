import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from typing import Dict, Any, List
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class BeehiivClient:
    BASE_URL = "https://api.beehiiv.com/v2"
    
    def __init__(self):
        if not hasattr(settings, 'BEEHIIV_API_KEY') or not settings.BEEHIIV_API_KEY:
            raise ValueError("BEEHIIV_API_KEY setting is required")
        if not hasattr(settings, 'BEEHIIV_PUBLICATION_ID') or not settings.BEEHIIV_PUBLICATION_ID:
            raise ValueError("BEEHIIV_PUBLICATION_ID setting is required")
        
        self.api_key = settings.BEEHIIV_API_KEY
        self.publication_id = settings.BEEHIIV_PUBLICATION_ID
        self.utm_source = getattr(settings, 'BEEHIIV_UTM_SOURCE', 'website')

        # Configure retry mechanism
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Exponential backoff factor (1s, 2s, 4s, etc.)
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.timeout = 10

    def _validate_email(self, email: str) -> None:
        """
        Validate the format of an email address using Django's built-in validator.
        
        Args:
            email (str): Email address to validate
            
        Raises:
            ValueError: If the email is not in a valid format
        """
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValueError(f"Invalid email format: {email}") from e

    def create_subscriber(self, email: str) -> Dict[str, Any]:
        """
        Create a new subscriber in Beehiiv.
        
        Args:
            email (str): Email address of the subscriber
            
        Returns:
            Dict[str, Any]: Response from Beehiiv API
            
        Raises:
            ValueError: If the email is not in a valid format
            requests.exceptions.RequestException: If API request fails
        """
        self._validate_email(email)
        
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
            "utm_source": self.utm_source
        }
        
        response = self.session.post(endpoint, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def bulk_create_subscribers(self, emails: List[str]) -> Dict[str, Any]:
        """
        Bulk create subscribers in Beehiiv.
        
        Args:
            emails (List[str]): List of email addresses
            
        Returns:
            Dict[str, Any]: Response from Beehiiv API
            
        Raises:
            ValueError: If the email list is empty, exceeds the batch size limit, or contains invalid emails
            requests.exceptions.RequestException: If API request fails
        """
        if not emails:
            raise ValueError("Email list cannot be empty")
        
        max_batch_size = getattr(settings, 'BEEHIIV_MAX_BATCH_SIZE', 1000)
        if len(emails) > max_batch_size:
            raise ValueError(f"Batch size exceeds maximum allowed ({max_batch_size})")
        
        for email in emails:
            self._validate_email(email)
        
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
            "utm_source": self.utm_source
        }
        
        response = self.session.post(endpoint, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()

    def get_subscriber(self, email: str) -> Dict[str, Any]:
        """
        Get subscriber details from Beehiiv.
        
        Args:
            email (str): Email address of the subscriber
            
        Returns:
            Dict[str, Any]: Response from Beehiiv API
            
        Raises:
            ValueError: If the email is not in a valid format
            requests.exceptions.RequestException: If API request fails
        """
        self._validate_email(email)
        
        endpoint = f"{self.BASE_URL}/publications/{self.publication_id}/subscriptions/email/{email}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = self.session.get(endpoint, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.json()