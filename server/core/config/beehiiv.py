from decouple import config

BEEHIIV_API_KEY = config('BEEHIIV_API_KEY', default=None)
BEEHIIV_PUBLICATION_ID = config('BEEHIIV_PUBLICATION_ID', default=None)
BEEHIIV_ENABLED = bool(config('BEEHIIV_ENABLED', default=False))
BEEHIIV_SYNC_BATCH_SIZE = int(config('BEEHIIV_SYNC_BATCH_SIZE', default=50))