
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

BOOKS = []
NEXT_ID = 1

@app.get("/")
def home():
    return render_template("index.html", books=BOOKS)

from flask import request, render_template, redirect, url_for
@app.route("/books/new", methods=["GET", "POST"])
def new_book():
    global NEXT_ID
    if request.method == "GET":
        return render_template("new_book.html")
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    BOOKS.append({"id": NEXT_ID, "title": title, "author": author})
    NEXT_ID += 1
    return redirect(url_for("home"))