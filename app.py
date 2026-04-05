from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

from main import (
    get_movie_data,
    download_poster,
    make_square,
    add_overlay,
    create_caption,
    post_to_instagram
)

app = Flask(__name__)
app.secret_key = "aipps_secret"

# 🔐 LOGIN
USERNAME = "admin"
PASSWORD = "1234"

DB = "movies.db"


# 🧠 INIT DATABASE
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT
        )
    """)

    conn.commit()
    conn.close()


# 💾 SAVE MOVIE
def save_movie(title):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("INSERT INTO movies (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()


# 📄 GET MOVIES
def get_movies():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT title FROM movies ORDER BY id DESC")
    movies = [row[0] for row in c.fetchall()]

    conn.close()
    return movies


# 🚀 MAIN LOGIC
def run_aipps(movie_name):
    movie = get_movie_data(movie_name)

    if not movie:
        return "❌ Movie not found"

    if not download_poster(movie["title"], movie["year"]):
        return "❌ Poster failed"

    make_square()
    add_overlay()

    caption = create_caption(movie)

    try:
        post_to_instagram(caption, movie["title"])
        save_movie(movie["title"])   # ✅ SAVE TO DB
        return "✅ Posted successfully!"
    except Exception as e:
        print(e)
        return "❌ Error posting"


# 🔐 LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username").strip()
        pwd = request.form.get("password").strip()

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


# 🏠 HOME
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

    movies = get_movies()

    return render_template(
        "index.html",
        message=message,
        status=status,
        movies=movies
    )


# 🚀 START
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)