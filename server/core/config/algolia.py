from decouple import config

ALGOLIA = {
    'APPLICATION_ID': config('ALGOLIA_APPLICATION_ID'),
    'API_KEY': config('ALGOLIA_API_KEY'),
}