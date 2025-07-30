import requests
from django.conf import settings
from django.utils import translation

BASE_URL = "https://api.themoviedb.org/3"

def tmdb_get(endpoint, params=None):
    if params is None:
        params = {}
    params['api_key'] = settings.TMDB_API_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    response.raise_for_status()
    return response.json()

def get_tmdb_language():
    """Get TMDB language code based on current Django language"""
    current_lang = translation.get_language()
    # Map Django language codes to TMDB language codes
    lang_mapping = {
        'en': 'en-US',
        'en-us': 'en-US',
        'fr': 'fr-FR',
        'fr-fr': 'fr-FR',
    }
    return lang_mapping.get(current_lang, 'en-US')

def fetch_popular_movies(page=1):
    return tmdb_get("movie/popular", {"page": page, "language": get_tmdb_language()})

def fetch_movie_details(tmdb_id):
    return tmdb_get(f"movie/{tmdb_id}", {"language": get_tmdb_language()})

def fetch_movie_credits(tmdb_id):
    return tmdb_get(f"movie/{tmdb_id}/credits")
