from flask import Flask, render_template, request, redirect, session
import os

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
app.secret_key = "aipps_secret"


# 🔐 SIMPLE LOGIN (change credentials here)
USERNAME = "admin"
PASSWORD = "1234"


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
    except:
        return "❌ Error posting"


# 🔐 LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == USERNAME and pwd == PASSWORD:
            session["user"] = user
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# 🏠 MAIN APP
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    message = ""
    status = ""

    if request.method == "POST":
        movie_name = request.form.get("movie")

        result = run_aipps(movie_name)

        if "successfully" in result:
            status = "success"
        else:
            status = "error"

        message = result

    # 📄 READ POSTED MOVIES
    movies = []
    if os.path.exists("posted.txt"):
        with open("posted.txt", "r") as f:
            movies = f.read().splitlines()[::-1]  # latest first

    return render_template("index.html", message=message, status=status, movies=movies)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)