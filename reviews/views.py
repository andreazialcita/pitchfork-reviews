from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect,  get_object_or_404
from django.http import HttpResponse

from .models import Review, Artist, Genre
from .forms import ReviewForm, ArtistForm, GenreForm

# Create your views here.


def addreview(request):
    if request.method == 'GET':
        cf = ReviewForm()
    elif request.method == 'POST':        
        cf = ReviewForm(request.POST)  
        if cf.is_valid():
            review = cf.save(commit=False)
            name = cf.cleaned_data['artist_name'].strip()
            artist = Artist.objects.filter(name__iexact=name).first()
            if not artist:
                artist = Artist.objects.create(name=name)
            review.artist = artist
            review.save()
            cf.save_m2m()  # save the genres ManyToMany relationship
            # messages.success(request, "Review added successfully.")
            return redirect("search")  # updated to use your reviews namespace

    artists = Artist.objects.order_by('name')
    context = {
        'form': cf,
        'actionname': "Add",
        'artists': artists,
    }
    return render(request, 'reviews/review_form.html', context)

def detailreview(request, pk):
    r = get_object_or_404(Review, id=pk)
    context = {'review': r}
    return render(request, 'reviews/review_detail.html', context)

def updatereview(request, pk):
    r = get_object_or_404(Review, id=pk)
    if request.method == "GET":
        form = ReviewForm(instance=r, initial={'artist_name': r.artist.name})
    elif request.method == "POST":
        form = ReviewForm(request.POST, instance=r)
        if form.is_valid():
            review = form.save(commit=False)
            name = form.cleaned_data['artist_name'].strip()
            artist = Artist.objects.filter(name__iexact=name).first()
            if not artist:
                artist = Artist.objects.create(name=name)
            review.artist = artist
            review.save()
            form.save_m2m()
            messages.success(request, "Review updated successfully")
            # return redirect('reviews:review-detail', pk=r.pk)

    artists = Artist.objects.order_by('name')
    context = {
        'form': form,
        'actionname': "Edit",
        'artists': artists,
    }
    return render(request, 'reviews/review_form.html', context)

def deletereview(request, pk):
    c = get_object_or_404(Review, id=pk)#Customer.objects.get(id=pk)
    if request.method == 'GET': #create a context object to pass values to the confirmation page
        context = { 'review': c}
        return render(request, 'reviews/review_delete.html', context)
    elif request.method == "POST": #they click yes
        c.delete()
        return redirect("search")