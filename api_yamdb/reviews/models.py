from django.db import models
from django.core.validators import MaxValueValidator

from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True,
    null=True, related_name='titles')
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)
    
    def __str__(self):
        return self.name  

class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    score = models.IntegerField(validators=[MaxValueValidator(10)])
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True) 
    
class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='titles')
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, related_name='genres', blank=True,
    null=True) 
    
    def __str__(self):
        return f'{self.title_id} {self.genre_id}'

class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)    
    
