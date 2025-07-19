from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/rate/', views.rate_movie, name='rate_movie'),
    path('recommendations/', views.recommendations, name='recommendations'),
]
