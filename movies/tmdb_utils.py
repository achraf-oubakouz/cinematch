import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"

def tmdb_get(endpoint, params=None):
    if params is None:
        params = {}
    params['api_key'] = settings.TMDB_API_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    response.raise_for_status()
    return response.json()

def fetch_popular_movies(page=1):
    return tmdb_get("movie/popular", {"page": page, "language": "en-US"})

def fetch_movie_details(tmdb_id):
    return tmdb_get(f"movie/{tmdb_id}", {"language": "en-US"})

def fetch_movie_credits(tmdb_id):
    return tmdb_get(f"movie/{tmdb_id}/credits")
