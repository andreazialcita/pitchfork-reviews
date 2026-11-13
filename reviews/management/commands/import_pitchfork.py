import sqlite3
from django.core.management.base import BaseCommand
from django.db import transaction
from reviews.models import Artist, Genre, Review

class Command(BaseCommand):
    help = "Import Pitchfork reviews from the Kaggle SQLite file"

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the Kaggle .sqlite file")

    def handle(self, *args, **opts):
        con = sqlite3.connect(opts["path"])
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        years = {r["reviewid"]: r["year"] for r in cur.execute(
            "SELECT reviewid, MIN(year) AS year FROM years GROUP BY reviewid")}
        labels = {r["reviewid"]: r["label"] for r in cur.execute(
            "SELECT reviewid, MIN(label) AS label FROM labels GROUP BY reviewid")}
        genres = {}
        for r in cur.execute("SELECT reviewid, genre FROM genres"):
            genres.setdefault(r["reviewid"], []).append(r["genre"] or "other")

        artist_cache, genre_cache = {}, {}
        with transaction.atomic():
            Review.objects.all().delete()   # makes the command safe to re-run
            for r in cur.execute("SELECT * FROM reviews"):
                rid = r["reviewid"]
                name = (r["artist"] or "Unknown").strip()
                if name not in artist_cache:
                    artist_cache[name] = Artist.objects.get_or_create(name=name)[0]

                review = Review.objects.create(
                    title=(r["title"] or "").strip(),
                    artist=artist_cache[name],
                    score=r["score"],
                    best_new_music=bool(r["best_new_music"]),
                    author=(r["author"] or "").strip(),
                    author_type=r["author_type"] or "Contributor",
                    label=(labels.get(rid) or "").strip() or "other",
                    release_year=years.get(rid),
                    pub_date=r["pub_date"],
                    pub_year=r["pub_year"],
                    url=r["url"] or "",
                )
                names = genres.get(rid) or ["other"]
                objs = []
                for g in names:
                    if g not in genre_cache:
                        genre_cache[g] = Genre.objects.get_or_create(name=g)[0]
                    objs.append(genre_cache[g])
                review.genres.set(objs)

        self.stdout.write(self.style.SUCCESS(f"Imported {Review.objects.count()} reviews"))