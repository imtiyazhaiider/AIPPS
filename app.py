from flask import Flask, render_template, request
import threading

# import your existing functions
from main import (
    get_movie_data,
    download_poster,
    make_square,
    add_overlay,
    create_caption,
    is_already_posted,
    post_to_instagram
)

app = Flask(__name__)


def run_aipps(movie_name):
    movie = get_movie_data(movie_name)

    if not movie:
        return "❌ Movie not found"

    if is_already_posted(movie["title"]):
        return "⚠️ Already posted"

    if not download_poster(movie["title"], movie["year"]):
        return "❌ Poster failed"

    make_square()
    add_overlay()

    caption = create_caption(movie)

    try:
        post_to_instagram(caption, movie["title"])
        return "✅ Posted successfully!"
    except Exception as e:
        print(e)
        return "❌ Error posting"


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        movie_name = request.form.get("movie")

        # run in background
        thread = threading.Thread(target=run_aipps, args=(movie_name,))
        thread.start()

        message = "⏳ Processing... check Instagram shortly"

    return render_template("index.html", message=message)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)