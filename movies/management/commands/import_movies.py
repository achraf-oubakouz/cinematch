from django.core.management.base import BaseCommand
from movies.tmdb_utils import fetch_popular_movies, fetch_movie_details, fetch_movie_credits
from movies.models import Movie

class Command(BaseCommand):
    help = "Import popular movies from TMDB into the database"

    def handle(self, *args, **kwargs):
        data = fetch_popular_movies()
        for movie_data in data.get('results', []):
            tmdb_id = movie_data['id']

            # Skip if movie already exists
            if Movie.objects.filter(tmdb_id=tmdb_id).exists():
                self.stdout.write(f"Movie {tmdb_id} already exists, skipping.")
                continue

            details = fetch_movie_details(tmdb_id)
            credits = fetch_movie_credits(tmdb_id)

            # Find the director's name
            director = "Unknown"
            for crew_member in credits.get('crew', []):
                if crew_member['job'] == 'Director':
                    director = crew_member['name']
                    break

            # Format genres as comma-separated string
            genres = ", ".join([g['name'] for g in details.get('genres', [])]) or "Unknown"

            # Extract release year from release date
            release_date = details.get('release_date', "")
            release_year = int(release_date[:4]) if release_date else 0

            # Build full poster URL
            poster_path = details.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

            # Create and save the movie
            Movie.objects.create(
                tmdb_id=tmdb_id,
                title=details.get('title', 'Untitled'),
                description=details.get('overview', ''),
                director=director,
                release_year=release_year,
                genre=genres,
                duration=details.get('runtime', 0),
                poster_url=poster_url,
            )
            self.stdout.write(self.style.SUCCESS(f"Imported: {details.get('title')}"))

        self.stdout.write(self.style.SUCCESS("Import complete."))
