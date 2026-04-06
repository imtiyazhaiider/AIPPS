import requests
import os
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")


def get_movie_data(name):
    url = f"http://www.omdbapi.com/?t={name}&apikey={OMDB_API_KEY}"
    data = requests.get(url).json()

    if data["Response"] == "False":
        return None

    return {
        "title": data["Title"],
        "year": data["Year"],
        "plot": data["Plot"],
        "rating": data["imdbRating"],
        "genre": data["Genre"]
    }


def download_poster(title, year):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    data = requests.get(url).json()

    results = data.get("results", [])
    if not results:
        return False

    best = results[0]

    for m in results:
        if m.get("release_date", "").startswith(year):
            best = m
            break

    path = best.get("poster_path")
    if not path:
        return False

    img_url = f"https://image.tmdb.org/t/p/original{path}"
    img = requests.get(img_url).content

    with open("poster.jpg", "wb") as f:
        f.write(img)

    return True


def make_square():
    img = Image.open("poster.jpg")
    size = max(img.size)
    new = Image.new("RGB", (size, size), (0, 0, 0))
    new.paste(img, ((size - img.width)//2, (size - img.height)//2))
    new.save("poster.jpg")


def add_overlay():
    img = Image.open("poster.jpg").convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle([(0, h-80), (w, h)], fill=(0, 0, 0, 180))

    text = "WATCHED • AIPPS"

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    draw.text((20, h-60), text, font=font, fill=(255,255,255))

    final = Image.alpha_composite(img, overlay)
    final.convert("RGB").save("poster.jpg")


def create_caption(movie):
    return f"""Just finished watching {movie['title']} ({movie['year']})

{movie['plot'][:120]}...

⭐ {movie['rating']} | {movie['genre']}

#watched #AIPPS"""


def post_to_instagram(caption, title):
    cl = Client()
    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.photo_upload("poster.jpg", caption)