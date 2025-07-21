from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from .models import Movie, Rating
from .forms import MovieRatingForm
from .recommender import MovieRecommender

def index(request):
    movies_list = Movie.objects.all()
    
    # Get filter parameters
    genre_filter = request.GET.get('genre', '')
    year_filter = request.GET.get('year', '')
    director_filter = request.GET.get('director', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort', 'title')
    
    # Apply filters
    if genre_filter:
        movies_list = movies_list.filter(genre__icontains=genre_filter)
    
    if year_filter:
        try:
            year = int(year_filter)
            movies_list = movies_list.filter(release_year=year)
        except ValueError:
            pass
    
    if director_filter:
        movies_list = movies_list.filter(director__icontains=director_filter)
    
    # Apply sorting
    if sort_by == 'title':
        movies_list = movies_list.order_by('title')
    elif sort_by == 'year_desc':
        movies_list = movies_list.order_by('-release_year')
    elif sort_by == 'year_asc':
        movies_list = movies_list.order_by('release_year')
    else:
        # Default to title sorting for consistent results
        movies_list = movies_list.order_by('title')
    
    # Add average rating to each movie and apply rating filter
    movies_with_ratings = []
    for movie in movies_list:
        avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
        movie.average_rating = avg_rating
        
        # Apply rating filter
        if rating_filter:
            try:
                min_rating = float(rating_filter)
                if avg_rating and avg_rating >= min_rating:
                    movies_with_ratings.append(movie)
                elif not avg_rating and min_rating == 0:  # Include unrated movies for "0+" filter
                    movies_with_ratings.append(movie)
            except ValueError:
                movies_with_ratings.append(movie)
        else:
            movies_with_ratings.append(movie)
    
    # Sort by rating if requested (after adding ratings)
    if sort_by == 'rating_desc':
        movies_with_ratings.sort(key=lambda x: x.average_rating or 0, reverse=True)
    elif sort_by == 'rating_asc':
        movies_with_ratings.sort(key=lambda x: x.average_rating or 0)
    
    # Get unique values for filter options
    # Extract individual genres from combined genre strings
    all_genre_strings = Movie.objects.values_list('genre', flat=True).distinct().exclude(genre__isnull=True).exclude(genre__exact='').exclude(genre__exact='Unknown')
    all_genres = set()
    for genre_string in all_genre_strings:
        if genre_string:
            # Split by comma and clean up each genre
            genres = [g.strip() for g in genre_string.split(',') if g.strip()]
            all_genres.update(genres)
    
    # Generate full year range from 1900 to current year + 1
    from datetime import datetime
    current_year = datetime.now().year
    all_years = list(range(current_year + 1, 1899, -1))  # From next year down to 1900
    
    all_directors = Movie.objects.values_list('director', flat=True).distinct().exclude(director__isnull=True).exclude(director__exact='').exclude(director__exact='Unknown')
    
    paginator = Paginator(movies_with_ratings, 12)  # Show 12 movies per page
    page_number = request.GET.get('page')
    movies = paginator.get_page(page_number)
    
    context = {
        'movies': movies,
        'all_genres': sorted(all_genres),
        'all_years': all_years,
        'all_directors': sorted(set([d for d in all_directors if d and d != 'Unknown']))[:20],  # Limit to top 20 directors
        'current_filters': {
            'genre': genre_filter,
            'year': year_filter,
            'director': director_filter,
            'rating': rating_filter,
            'sort': sort_by,
        }
    }
    
    return render(request, 'movies/index.html', context)

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
    # Prepare data for user profile
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie').order_by('-created_at')
    total_ratings = user_ratings.count()
    avg_rating = user_ratings.aggregate(Avg('rating'))['rating__avg']
    
    high_rated_movies = user_ratings.filter(rating__gte=4)
    favorite_genres = {}
    for rating in high_rated_movies:
        genre = rating.movie.genre
        favorite_genres[genre] = favorite_genres.get(genre, 0) + 1
    favorite_genres = sorted(favorite_genres.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Prepare admin data
    total_users, total_movies, total_ratings_all = None, None, None
    recently_joined, recent_movies = None, None
    if request.user.is_staff:
        total_users = User.objects.count()
        total_movies = Movie.objects.count()
        total_ratings_all = Rating.objects.count()
        recently_joined = User.objects.order_by('-date_joined')[:5]
        recent_movies = Movie.objects.order_by('-created_at')[:5]
        
    context = {
        'user_ratings': user_ratings[:10],
        'total_ratings': total_ratings,
        'avg_rating': avg_rating,
        'favorite_genres': favorite_genres,
        'total_users': total_users,
        'total_movies': total_movies,
        'total_ratings_all': total_ratings_all,
        'recent_users': recently_joined,
        'recent_movies': recent_movies,
    }

    return render(request, 'movies/profile.html', context)

@staff_member_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Add rating count to each user
    for user in users:
        user.rating_count = Rating.objects.filter(user=user).count()
        user.avg_rating = Rating.objects.filter(user=user).aggregate(Avg('rating'))['rating__avg']
    
    paginator = Paginator(users, 20)  # Show 20 users per page
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    return render(request, 'movies/admin_users.html', {
        'users': users_page,
        'total_users': User.objects.count(),
    })

@staff_member_required
def admin_movies(request):
    movies = Movie.objects.all().order_by('-created_at')
    
    # Add rating stats to each movie
    for movie in movies:
        movie.rating_count = Rating.objects.filter(movie=movie).count()
        movie.avg_rating = Rating.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
    
    paginator = Paginator(movies, 20)  # Show 20 movies per page
    page_number = request.GET.get('page')
    movies_page = paginator.get_page(page_number)
    
    return render(request, 'movies/admin_movies.html', {
        'movies': movies_page,
        'total_movies': Movie.objects.count(),
    })

@staff_member_required
def add_movie(request):
    if request.method == 'POST':
        # Handle form submission for adding a new movie
        title = request.POST.get('title')
        description = request.POST.get('description')
        director = request.POST.get('director')
        release_year = request.POST.get('release_year')
        genre = request.POST.get('genre')
        duration = request.POST.get('duration')
        poster_url = request.POST.get('poster_url')
        
        if title and release_year:
            Movie.objects.create(
                title=title,
                description=description or '',
                director=director or 'Unknown',
                release_year=int(release_year),
                genre=genre or 'Unknown',
                duration=int(duration) if duration else 0,
                poster_url=poster_url or ''
            )
            messages.success(request, f'Movie "{title}" has been added successfully!')
            return redirect('movies:admin_movies')
        else:
            messages.error(request, 'Title and release year are required.')
    
    return render(request, 'movies/add_movie.html')

@staff_member_required
def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        # Handle form submission for editing a movie
        title = request.POST.get('title')
        description = request.POST.get('description')
        director = request.POST.get('director')
        release_year = request.POST.get('release_year')
        genre = request.POST.get('genre')
        duration = request.POST.get('duration')
        poster_url = request.POST.get('poster_url')
        
        if title and release_year:
            movie.title = title
            movie.description = description or ''
            movie.director = director or 'Unknown'
            movie.release_year = int(release_year)
            movie.genre = genre or 'Unknown'
            movie.duration = int(duration) if duration else 0
            movie.poster_url = poster_url or ''
            movie.save()
            
            messages.success(request, f'Movie "{title}" has been updated successfully!')
            return redirect('movies:admin_movies')
        else:
            messages.error(request, 'Title and release year are required.')
    
    return render(request, 'movies/edit_movie.html', {'movie': movie})

@staff_member_required
def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        movie_title = movie.title
        movie.delete()
        messages.success(request, f'Movie "{movie_title}" has been deleted successfully!')
        return redirect('movies:admin_movies')
    
    return render(request, 'movies/delete_movie.html', {'movie': movie})

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Handle form submission for editing a user
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        
        if username:
            # Check if username is taken by another user
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, 'Username is already taken.')
            else:
                user.username = username
                user.email = email or ''
                user.first_name = first_name or ''
                user.last_name = last_name or ''
                user.is_staff = is_staff
                user.is_active = is_active
                user.save()
                
                messages.success(request, f'User "{username}" has been updated successfully!')
                return redirect('movies:admin_users')
        else:
            messages.error(request, 'Username is required.')
    
    return render(request, 'movies/edit_user.html', {'user_obj': user})

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('movies:admin_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted successfully!')
        return redirect('movies:admin_users')
    
    return render(request, 'movies/delete_user.html', {'user_obj': user})
