from django.db import models

# reviews/models.py
from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=300, unique=True)
    def __str__(self): return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Review(models.Model):
    title = models.CharField(max_length=300)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="reviews")
    genres = models.ManyToManyField(Genre, blank=True, related_name="reviews")
    score = models.FloatField()
    best_new_music = models.BooleanField(default=False)
    author = models.CharField(max_length=200, blank=True)
    author_type = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=200, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    pub_date = models.DateField()
    pub_year = models.IntegerField()
    url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ["-pub_date"]
    def __str__(self): return f"{self.title} ({self.artist})"