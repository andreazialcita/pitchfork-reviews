from django.forms import ModelForm, HiddenInput
from .models import Artist, Genre, Review
from django import forms

class ReviewForm(ModelForm):
    artist_name = forms.CharField(
        max_length=300,
        label="Artist",
        widget=forms.TextInput(attrs={'list': 'artist-list', 'autocomplete': 'off'})
    )

    class Meta:
        model = Review
        fields = [
            'title',
            # 'artist' is handled via artist_name in the view
            'genres',
            'score',
            'best_new_music',
            'author',
            'author_type',
            'label',
            'release_year',
            'pub_date',
            'pub_year',
            'url',
        ]

class ArtistForm(ModelForm):
    class Meta:
        model = Artist
        fields = ['name'] 

class GenreForm(ModelForm):
    class Meta:
        model = Genre
        fields = ['name']
