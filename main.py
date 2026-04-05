import requests
from instagrapi import Client
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")


def get_movie_data(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["Response"] == "False":
        print("❌ Movie not found!")
        return None

    return {
        "title": data.get("Title", "Unknown"),
        "year": data.get("Year", ""),
        "plot": data.get("Plot", ""),
        "rating": data.get("imdbRating", "N/A"),
        "genre": data.get("Genre", "N/A")
    }


# 🔥 Improved TMDb poster (accurate matching)
def download_poster(movie_title, movie_year):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(search_url).json()

    results = response.get("results", [])

    if not results:
        print("❌ No TMDb results found")
        return False

    best_match = None

    for movie in results:
        title = movie.get("title", "").lower()
        release_date = movie.get("release_date", "")

        year = release_date[:4] if release_date else ""

        if movie_title.lower() in title:
            if year == movie_year:
                best_match = movie
                break

            if not best_match:
                best_match = movie

    if not best_match:
        best_match = results[0]

    poster_path = best_match.get("poster_path")

    if not poster_path:
        print("❌ No poster found")
        return False

    poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"

    img_data = requests.get(poster_url).content

    with open("poster.jpg", "wb") as f:
        f.write(img_data)

    print("🔥 Accurate HD Poster downloaded")
    return True


# 🟦 Make square (no crop)
def make_square():
    img = Image.open("poster.jpg").convert("RGB")
    size = max(img.size)

    new_img = Image.new("RGB", (size, size), (0, 0, 0))
    new_img.paste(img, ((size - img.width) // 2, (size - img.height) // 2))

    new_img.save("poster.jpg")


# 🎨 Overlay
def add_overlay():
    image = Image.open("poster.jpg").convert("RGBA")
    width, height = image.size

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    rect_height = int(height * 0.10)
    draw.rectangle(
        [(0, height - rect_height), (width, height)],
        fill=(0, 0, 0, 180)
    )

    text = "Posted by AIPPS"

    try:
        font = ImageFont.truetype("arial.ttf", int(height * 0.03))
    except:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]

    text_x = (width - text_width) // 2
    text_y = height - rect_height + (rect_height - text_height) // 2

    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

    final = Image.alpha_composite(image, overlay)
    final.convert("RGB").save("poster.jpg")

    print("🎨 Overlay added")


def shorten_plot(plot):
    if plot == "N/A" or not plot:
        return "A story worth watching."
    return plot.split(".")[0] + "."


def get_genre_emoji(genre):
    if "Action" in genre:
        return "🔥"
    elif "Comedy" in genre:
        return "😂"
    elif "Horror" in genre:
        return "👻"
    elif "Romance" in genre:
        return "❤️"
    elif "Sci-Fi" in genre:
        return "🚀"
    else:
        return "🎬"


def create_caption(movie):
    short_plot = shorten_plot(movie["plot"])
    emoji = get_genre_emoji(movie["genre"])

    rating = movie["rating"] if movie["rating"] != "N/A" else "Not rated"

    caption = f"""Just finished watching {movie['title']} ({movie['year']}) {emoji}

{short_plot}

⭐ {rating} | {movie['genre']}

— Powered by AIPPS

#watched #AIPPS #moviebuff #cinema #movienight #instamovies"""
    return caption


def is_already_posted(title):
    if not os.path.exists("posted.txt"):
        return False

    with open("posted.txt", "r") as f:
        posted = f.read().splitlines()

    return title.lower() in [x.lower() for x in posted]


def save_posted(title):
    with open("posted.txt", "a") as f:
        f.write(title + "\n")


def post_to_instagram(caption, title):
    cl = Client()

    print("🔐 Logging in...")
    cl.login(IG_USERNAME, IG_PASSWORD)

    print("📤 Posting...")
    cl.photo_upload("poster.jpg", caption)

    save_posted(title)

    print("✅ Posted successfully!")


def main():
    movie_name = input("Enter movie name: ")

    movie = get_movie_data(movie_name)

    if movie:
        if is_already_posted(movie["title"]):
            print("⚠️ Already posted!")
            return

        if not download_poster(movie["title"], movie["year"]):
            return

        make_square()
        add_overlay()

        caption = create_caption(movie)

        print("\n📄 Preview:\n")
        print(caption)

        if input("\nPost? (y/n): ").lower() == "y":
            post_to_instagram(caption, movie["title"])
        else:
            print("❌ Cancelled")


if __name__ == "__main__":
    main()