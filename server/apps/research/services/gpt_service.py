import re
from django.conf import settings
from openai import AsyncOpenAI

class GPTService:
    """Service for handling OpenAI GPT API interactions."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"
        self.max_tokens = 500

    async def prompt(self, system: str, user: str) -> str:
        """
        Send a prompt to GPT and get the response.
        
        Args:
            system (str): The system message that sets the behavior of the assistant
            user (str): The user's input/question
            
        Returns:
            str: The generated response from GPT
            
        Raises:
            Exception: If there's an error in the API call or if the API key is not set
        """
        if not settings.OPENAI_API_KEY:
            raise Exception("OpenAI API key is not configured")

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": self.clear_message(user)}
                ],
                max_tokens=self.max_tokens
            )
            # Access the response content directly from the completion object
            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            raise Exception(f"Error calling OpenAI API: {str(e)}")

    def clear_message(self, message: str) -> str:
        """Clear the message of any HTML tags, line breaks and multiple whitespaces, replacing them with a single space."""
        # First remove HTML tags and newlines
        cleaned = re.sub(r'<[^>]*>|\n', ' ', message)
        # Then replace multiple whitespaces with a single space
        return re.sub(r'\s+', ' ', cleaned).strip()

