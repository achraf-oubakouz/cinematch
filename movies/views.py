from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from .models import Movie, Rating
from .forms import MovieRatingForm
from .recommender import MovieRecommender

def index(request):
    movies_list = Movie.objects.all().order_by('-id')
    
    # Add average rating to each movie
    for movie in movies_list:
        movie.average_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    
    paginator = Paginator(movies_list, 12)  # Show 12 movies per page
    page_number = request.GET.get('page')
    movies = paginator.get_page(page_number)
    
    return render(request, 'movies/index.html', {'movies': movies})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Calculate average rating and total ratings
    ratings = Rating.objects.filter(movie=movie)
    movie.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    movie.total_ratings = ratings.count()
    
    # Get recent reviews
    reviews = ratings.select_related('user').order_by('-created_at')[:10]
    
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'reviews': reviews
    })

@login_required
def rate_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Check if user has already rated this movie
    existing_rating = Rating.objects.filter(user=request.user, movie=movie).first()
    
    if request.method == 'POST':
        form = MovieRatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']
            review_text = form.cleaned_data['review']
            
            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating_value
                existing_rating.review = review_text
                existing_rating.save()
                messages.success(request, 'Your rating has been updated!')
            else:
                # Create new rating
                Rating.objects.create(
                    user=request.user,
                    movie=movie,
                    rating=rating_value,
                    review=review_text
                )
                messages.success(request, 'Your rating has been submitted!')
            
            return redirect('movies:movie_detail', movie_id=movie.id)
    else:
        # Pre-fill form with existing rating if available
        initial_data = {}
        if existing_rating:
            initial_data['rating'] = existing_rating.rating
            initial_data['review'] = existing_rating.review
        form = MovieRatingForm(initial=initial_data)
    
    return render(request, 'movies/rate_movie.html', {
        'movie': movie,
        'form': form,
        'existing_rating': existing_rating
    })

@login_required
def recommendations(request):
    recommender = MovieRecommender()
    recommended_movies = recommender.get_recommendations(request.user.id, num_recommendations=12)
    
    # Add average rating to each movie
    for movie in recommended_movies:
        movie.average_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    
    return render(request, 'movies/recommendations.html', {
        'recommendations': recommended_movies
    })

def search_movies(request):
    query = request.GET.get('q')
    movies_list = []
    if query:
        movies_list = Movie.objects.filter(
            Q(title__icontains=query) | 
            Q(genre__icontains=query) |
            Q(director__icontains=query)
        ).order_by('title')
        
        # Add average rating to each movie
        for movie in movies_list:
            movie.average_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    
    return render(request, 'movies/search_results.html', {
        'movies': movies_list,
        'query': query
    })

@login_required
def profile(request):
    # Get user's ratings
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie').order_by('-created_at')
    
    # Calculate user stats
    total_ratings = user_ratings.count()
    avg_rating = user_ratings.aggregate(Avg('rating'))['rating__avg']
    
    # Get user's favorite genres based on highly rated movies
    high_rated_movies = user_ratings.filter(rating__gte=4)
    favorite_genres = {}
    for rating in high_rated_movies:
        genre = rating.movie.genre
        if genre in favorite_genres:
            favorite_genres[genre] += 1
        else:
            favorite_genres[genre] = 1
    
    # Sort genres by frequency
    favorite_genres = sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return render(request, 'movies/profile.html', {
        'user_ratings': user_ratings[:10],  # Show last 10 ratings
        'total_ratings': total_ratings,
        'avg_rating': avg_rating,
        'favorite_genres': favorite_genres,
    })
