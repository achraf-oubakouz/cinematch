from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_movies, name='search'),
    
    # Admin URLs
    path('manage/users/', views.admin_users, name='admin_users'),
    path('manage/movies/', views.admin_movies, name='admin_movies'),
    path('manage/add-movie/', views.add_movie, name='add_movie'),
    path('manage/edit-movie/<int:movie_id>/', views.edit_movie, name='edit_movie'),
    path('manage/delete-movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('manage/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]
