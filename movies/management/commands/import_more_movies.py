import os
import django
import requests

from django.core.management.base import BaseCommand
from movies.models import Movie

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cinematch.settings")
django.setup()

# TMDB API settings
TMDB_API_KEY = '718d6ac9c6465ad95bac344be466fce9'
TMDB_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'
TMDB_MOVIE_DETAILS_URL = 'https://api.themoviedb.org/3/movie/{}'
TMDB_CREDITS_URL = 'https://api.themoviedb.org/3/movie/{}/credits'

# 📝 Your movie titles here
MOVIE_TITLES = [
    "Inception",
    "Interstellar",
    "The Dark Knight",
    "The Matrix",
    "Fight Club"
]

class Command(BaseCommand):
    help = "Import specific movies by title from TMDB"

    def handle(self, *args, **options):
        for title in MOVIE_TITLES:
            # Search by title
            search_params = {'api_key': TMDB_API_KEY, 'query': title}
            search_response = requests.get(TMDB_SEARCH_URL, params=search_params)
            results = search_response.json().get('results')

            if not results:
                self.stdout.write(self.style.ERROR(f"Movie not found: {title}"))
                continue

            movie_data = results[0]
            movie_id = movie_data['id']

            # Get movie details
            details_response = requests.get(
                TMDB_MOVIE_DETAILS_URL.format(movie_id),
                params={'api_key': TMDB_API_KEY}
            )
            details = details_response.json()

            # Get credits for director
            credits_response = requests.get(
                TMDB_CREDITS_URL.format(movie_id),
                params={'api_key': TMDB_API_KEY}
            )
            credits = credits_response.json()

            director = "Unknown"
            for member in credits.get('crew', []):
                if member.get('job') == 'Director':
                    director = member.get('name')
                    break

            # Create movie in DB
            Movie.objects.update_or_create(
                title=details.get('title'),
                defaults={
                    'description': details.get('overview', ''),
                    'release_year': details.get('release_date', '')[:4],
                    'genre': ', '.join([g['name'] for g in details.get('genres', [])]),
                    'director': director,
                    'duration': details.get('runtime') or 0,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}" if details.get('poster_path') else ''
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Added movie: {title}"))
