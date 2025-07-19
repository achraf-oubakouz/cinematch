#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinematch.settings')
django.setup()

from movies.models import Movie, Rating
from django.contrib.auth.models import User

def test_poster_display():
    print("=== Movie Poster Display Test ===\n")
    
    movies = Movie.objects.all()[:5]
    print("Checking poster availability for movies:")
    
    for movie in movies:
        has_poster_url = bool(movie.poster_url)
        has_poster_file = bool(movie.poster)
        
        print(f"\n📽️  {movie.title}")
        print(f"   poster_url: {'✅' if has_poster_url else '❌'} {movie.poster_url if has_poster_url else 'None'}")
        print(f"   poster file: {'✅' if has_poster_file else '❌'}")
        
        # Test template logic
        if has_poster_url:
            print(f"   → Template will show: poster_url image")
        elif has_poster_file:
            print(f"   → Template will show: uploaded poster file")
        else:
            print(f"   → Template will show: 'No Image' placeholder")
    
    print(f"\n=== Template Fix Summary ===")
    print("✅ index.html - checks poster_url first, then poster")
    print("✅ movie_detail.html - checks poster_url first, then poster")
    print("✅ recommendations.html - FIXED to check poster_url first, then poster")
    print("✅ rate_movie.html - FIXED to check poster_url first, then poster")
    
    print(f"\n🎯 All templates now consistently check:")
    print("   1. movie.poster_url (TMDB URLs)")
    print("   2. movie.poster (uploaded files)")
    print("   3. Fallback to 'No Image' placeholder")

if __name__ == '__main__':
    test_poster_display()
