import os

BEEHIIV_CONFIG = {
    'API_KEY': os.getenv('BEEHIIV_API_KEY', ''),
    'PUBLICATION_ID': os.getenv('BEEHIIV_PUBLICATION_ID', '')
}