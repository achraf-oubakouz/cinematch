#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinematch.settings')
django.setup()

from movies.models import Movie, Rating
from django.contrib.auth.models import User
from movies.recommender import MovieRecommender

def test_recommendation_system():
    print("=== Cinematch Recommendation System Analysis ===\n")
    
    # Check database contents
    print("Database Statistics:")
    print(f"- Movies: {Movie.objects.count()}")
    print(f"- Users: {User.objects.count()}")
    print(f"- Ratings: {Rating.objects.count()}\n")
    
    # Show sample data
    print("Sample Movies:")
    for movie in Movie.objects.all()[:5]:
        ratings = Rating.objects.filter(movie=movie)
        avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
        print(f"- {movie.title} ({movie.release_year}) - Avg Rating: {avg_rating:.1f}/5.0 ({len(ratings)} ratings)")
    
    if Rating.objects.count() == 0:
        print("\n❌ No ratings found in database. Recommendations will fall back to popular movies.")
        return
    
    print(f"\nSample Ratings:")
    for rating in Rating.objects.all()[:5]:
        print(f"- {rating.user.username} rated '{rating.movie.title}': {rating.rating}/5")
    
    # Test recommendation system
    print(f"\n=== Testing Recommendation System ===")
    recommender = MovieRecommender()
    
    # Test with first user
    first_user = User.objects.first()
    if first_user:
        print(f"\nTesting recommendations for user: {first_user.username}")
        
        try:
            # Test building ratings matrix
            print("Building ratings matrix...")
            ratings_matrix = recommender.build_ratings_matrix()
            if ratings_matrix.empty:
                print("❌ Ratings matrix is empty")
                return
            else:
                print(f"✅ Ratings matrix built: {ratings_matrix.shape[0]} users × {ratings_matrix.shape[1]} movies")
            
            # Test similarity calculation
            print("Calculating user similarities...")
            user_similarity = recommender.calculate_user_similarity()
            if user_similarity is not None:
                print(f"✅ User similarity matrix computed: {user_similarity.shape}")
            else:
                print("❌ Failed to compute user similarities")
                return
            
            # Test recommendations
            print("Generating recommendations...")
            recommendations = recommender.get_recommendations(first_user.id, num_recommendations=5)
            
            if recommendations:
                print(f"✅ Generated {len(recommendations)} recommendations:")
                for i, movie in enumerate(recommendations, 1):
                    print(f"  {i}. {movie.title} ({movie.release_year})")
            else:
                print("❌ No recommendations generated")
                
        except Exception as e:
            print(f"❌ Error testing recommendations: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No users found in database")

if __name__ == '__main__':
    test_recommendation_system()
