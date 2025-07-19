from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    director = models.CharField(max_length=255, default='Unknown')
    release_year = models.IntegerField()
    genre = models.CharField(max_length=100, default='Unknown')
    duration = models.IntegerField(default=0, help_text='Duration in minutes')
    poster = models.ImageField(upload_to='movie_posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'movie')
        
    def __str__(self):
        return f'{self.user.username} rated {self.movie.title}: {self.rating}/5'
