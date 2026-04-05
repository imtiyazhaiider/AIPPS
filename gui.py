import tkinter as tk
from tkinter import messagebox
import threading

# Import your existing functions
from main import (
    get_movie_data,
    download_poster,
    make_square,
    add_overlay,
    create_caption,
    is_already_posted,
    post_to_instagram
)


def run_aipps(movie_name, status_label):
    status_label.config(text="⏳ Processing...")

    movie = get_movie_data(movie_name)

    if not movie:
        status_label.config(text="❌ Movie not found")
        return

    if is_already_posted(movie["title"]):
        status_label.config(text="⚠️ Already posted")
        return

    if not download_poster(movie["title"], movie["year"]):
        status_label.config(text="❌ Poster failed")
        return

    make_square()
    add_overlay()

    caption = create_caption(movie)

    try:
        post_to_instagram(caption, movie["title"])
        status_label.config(text="✅ Posted successfully!")
    except Exception as e:
        status_label.config(text="❌ Error posting")
        print(e)


def start_process(entry, status_label):
    movie_name = entry.get()

    if not movie_name:
        messagebox.showwarning("Input Error", "Please enter a movie name")
        return

    # Run in separate thread (prevents freezing)
    threading.Thread(
        target=run_aipps,
        args=(movie_name, status_label),
        daemon=True
    ).start()


# 🎨 GUI Setup
root = tk.Tk()
root.title("AIPPS 🎬")
root.geometry("400x250")
root.resizable(False, False)

# Title
title_label = tk.Label(root, text="AIPPS", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

# Input
entry = tk.Entry(root, width=30, font=("Arial", 12))
entry.pack(pady=10)
entry.insert(0, "Enter movie name...")

# Button
post_button = tk.Button(
    root,
    text="Post to Instagram",
    font=("Arial", 12),
    command=lambda: start_process(entry, status_label)
)
post_button.pack(pady=10)

# Status
status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack(pady=10)

# Run app
root.mainloop()