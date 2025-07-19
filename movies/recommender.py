import pandas as pd
from django.contrib.auth.models import User
from .models import Movie, Rating
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MovieRecommender:
    def __init__(self):
        self.ratings_matrix = None
        self.user_similarity = None
        
    def build_ratings_matrix(self):
        """Build user-movie ratings matrix"""
        ratings = Rating.objects.all().select_related('user', 'movie')
        
        # Create a DataFrame with user ratings
        data = []
        for rating in ratings:
            data.append({
                'user_id': rating.user.id,
                'movie_id': rating.movie.id,
                'rating': rating.rating
            })
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Create pivot table (users as rows, movies as columns)
        self.ratings_matrix = df.pivot(index='user_id', columns='movie_id', values='rating')
        self.ratings_matrix = self.ratings_matrix.fillna(0)
        
        return self.ratings_matrix
    
    def calculate_user_similarity(self):
        """Calculate cosine similarity between users"""
        if self.ratings_matrix is None or self.ratings_matrix.empty:
            return None
            
        # Calculate cosine similarity between users
        self.user_similarity = cosine_similarity(self.ratings_matrix)
        return self.user_similarity
    
    def get_recommendations(self, user_id, num_recommendations=5):
        """Get movie recommendations for a user using collaborative filtering"""
        self.build_ratings_matrix()
        
        if self.ratings_matrix is None or self.ratings_matrix.empty:
            # If no ratings exist, return popular movies
            return self.get_popular_movies(num_recommendations)
        
        if user_id not in self.ratings_matrix.index:
            # If user hasn't rated any movies, return popular movies
            return self.get_popular_movies(num_recommendations)
        
        self.calculate_user_similarity()
        
        # Get user's index in the matrix
        user_index = list(self.ratings_matrix.index).index(user_id)
        
        # Get similar users
        user_similarities = self.user_similarity[user_index]
        
        # Get user's ratings
        user_ratings = self.ratings_matrix.iloc[user_index]
        
        # Calculate weighted scores for unrated movies
        recommendations = {}
        
        for movie_id in self.ratings_matrix.columns:
            if user_ratings[movie_id] == 0:  # User hasn't rated this movie
                weighted_score = 0
                similarity_sum = 0
                
                for other_user_idx, similarity in enumerate(user_similarities):
                    if other_user_idx != user_index and similarity > 0:
                        other_user_rating = self.ratings_matrix.iloc[other_user_idx][movie_id]
                        if other_user_rating > 0:
                            weighted_score += similarity * other_user_rating
                            similarity_sum += similarity
                
                if similarity_sum > 0:
                    recommendations[movie_id] = weighted_score / similarity_sum
        
        # Sort recommendations by score
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        # Get top recommendations
        top_movie_ids = [movie_id for movie_id, score in sorted_recommendations[:num_recommendations]]
        
        # Return Movie objects
        return Movie.objects.filter(id__in=top_movie_ids)
    
    def get_popular_movies(self, num_recommendations=5):
        """Get popular movies based on average ratings"""
        movies = Movie.objects.all()
        movie_scores = []
        
        for movie in movies:
            ratings = Rating.objects.filter(movie=movie)
            if ratings.exists():
                avg_rating = sum(r.rating for r in ratings) / ratings.count()
                movie_scores.append((movie, avg_rating, ratings.count()))
        
        # Sort by average rating and number of ratings
        movie_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        return [movie for movie, _, _ in movie_scores[:num_recommendations]]
