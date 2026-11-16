from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.http import HttpResponse
from django.shortcuts import render
from matplotlib.figure import Figure

from .models import Artist, Genre, Review

# (value passed to order_by, label shown in the dropdown)
SORT_CHOICES = [
    ("-pub_date", "Publication date (newest first)"),
    ("pub_date", "Publication date (oldest first)"),
    ("-score", "Score (high to low)"),
    ("score", "Score (low to high)"),
    ("-release_year", "Release year (newest first)"),
    ("release_year", "Release year (oldest first)"),
]


def search(request):
    """Search and filter reviews using the values from the GET form."""
    q = request.GET.get("q", "")
    genre = request.GET.get("genre", "")
    min_score = request.GET.get("min_score", "")
    max_score = request.GET.get("max_score", "")
    min_year = request.GET.get("min_year", "")
    max_year = request.GET.get("max_year", "")
    author = request.GET.get("author", "")
    sort = request.GET.get("sort", "-pub_date")

    # Start with every review and narrow it down with each filled-in field
    reviews = Review.objects.all()
    if q:
        reviews = reviews.filter(Q(title__icontains=q) | Q(artist__name__icontains=q))
    if genre:
        reviews = reviews.filter(genres__name=genre)
    if min_score:
        reviews = reviews.filter(score__gte=min_score)
    if max_score:
        reviews = reviews.filter(score__lte=max_score)
    if min_year:
        reviews = reviews.filter(pub_year__gte=min_year)
    if max_year:
        reviews = reviews.filter(pub_year__lte=max_year)
    if author:
        reviews = reviews.filter(author__icontains=author)

    valid_sorts = [value for value, label in SORT_CHOICES]
    if sort not in valid_sorts:
        sort = "-pub_date"
    if "release_year" in sort:
        reviews = reviews.exclude(release_year=None)  # about 406 reviews have no release year
    reviews = reviews.order_by(sort, "title")

    page = Paginator(reviews, 25).get_page(request.GET.get("page"))

    # Keep the current filters in the next/previous page links
    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "page": page,
        "querystring": params.urlencode(),
        "genres": Genre.objects.order_by("name"),
        "sort_choices": SORT_CHOICES,
        "q": q,
        "genre": genre,
        "min_score": min_score,
        "max_score": max_score,
        "min_year": min_year,
        "max_year": max_year,
        "author": author,
        "sort": sort,
    }
    return render(request, "reviews/search.html", context)


def year_averages():
    """Average score and number of reviews for each publication year."""
    return (
        Review.objects.values("pub_year")
        .annotate(avg_score=Avg("score"), num_reviews=Count("id"))
        .order_by("pub_year")
    )


def stats(request):
    """Aggregate statistics about the reviews."""
    # Average score and count per genre ("other" means the review had no genre)
    genre_stats = (
        Genre.objects.exclude(name="other")
        .annotate(avg_score=Avg("reviews__score"), num_reviews=Count("reviews"))
        .order_by("-avg_score")
    )

    # Artists with the most reviews ("various artists" is compilations, not one artist)
    top_artists = (
        Artist.objects.exclude(name="various artists")
        .annotate(num_reviews=Count("reviews"), avg_score=Avg("reviews__score"))
        .order_by("-num_reviews")[:10]
    )

    # Top 10 albums, optionally limited to one genre and/or one release year
    top_genre = request.GET.get("top_genre", "")
    top_year = request.GET.get("top_year", "")
    top_albums = Review.objects.all()
    if top_genre:
        top_albums = top_albums.filter(genres__name=top_genre)
    if top_year:
        top_albums = top_albums.filter(release_year=top_year)
    top_albums = top_albums.order_by("-score", "title")[:10]

    # Average score by the gap between release year and review year (gap > 0 means a reissue/look back)
    gap_stats = (
        Review.objects.exclude(release_year=None)
        .annotate(gap=F("pub_year") - F("release_year"))
        .filter(gap__gte=0)
        .values("gap")
        .annotate(avg_score=Avg("score"), num_reviews=Count("id"))
        .order_by("gap")
    )

    context = {
        "genre_stats": genre_stats,
        "year_stats": year_averages(),
        "top_artists": top_artists,
        "top_albums": top_albums,
        "top_genre": top_genre,
        "top_year": top_year,
        "genres": Genre.objects.exclude(name="other").order_by("name"),
        "gap_stats": gap_stats,
    }
    return render(request, "reviews/stats.html", context)


def stats_plot(request):
    """PNG line chart of the average score per publication year."""
    rows = year_averages()
    years = [row["pub_year"] for row in rows]
    scores = [row["avg_score"] for row in rows]

    fig = Figure(figsize=(8, 4))
    ax = fig.subplots()
    ax.plot(years, scores, marker="o")
    ax.set_xticks(years)  # one tick per year, shown as whole numbers
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Average score")
    ax.set_title("Average Pitchfork score by year")
    ax.grid(True)
    fig.tight_layout()

    response = HttpResponse(content_type="image/png")
    fig.savefig(response, format="png")
    return response
