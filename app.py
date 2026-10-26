import os
import uuid
from decimal import Decimal, InvalidOperation

from flask import (Flask, flash, redirect, render_template, request,
                   url_for)
from pymysql import MySQLError
from werkzeug.utils import secure_filename

import db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB uploads

UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------- helpers ----------
def save_image(field):
    """Save an uploaded image (bonus). Returns the stored file name or None."""
    f = request.files.get(field)
    if not f or not f.filename:
        return None
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED:
        flash("Image must be png, jpg, jpeg, gif or webp.", "error")
        return None
    name = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_DIR, name))
    return name


def remove_image(name):
    if name:
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(path):
            os.remove(path)


def parse_price(text):
    try:
        price = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        return None
    return price if price > 0 else None


# ---------- home ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- F2.1 show ----------
@app.route("/books")
def books():
    rows = db.query("SELECT * FROM Book ORDER BY book_id")
    return render_template("books.html", books=rows)


@app.route("/authors")
def authors():
    rows = db.query("SELECT * FROM Author ORDER BY author_id")
    return render_template("authors.html", authors=rows)


# ---------- F2.2 add / F2.3 edit book ----------
@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    authors_list = db.query("SELECT author_id, name FROM Author ORDER BY name")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price = parse_price(request.form.get("price", ""))
        author_id = request.form.get("author_id", "")
        if not title or price is None or not author_id.isdigit():
            flash("Title, a valid price and an author are required.", "error")
            return render_template("book_form.html", book=request.form,
                                   authors=authors_list, mode="Add")
        cover = save_image("cover")
        try:
            db.execute(
                "INSERT INTO Book (title, price, author_id, image_url) "
                "VALUES (%s, %s, %s, %s)", (title, price, int(author_id), cover))
        except MySQLError as e:
            remove_image(cover)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("book_form.html", book=request.form,
                                   authors=authors_list, mode="Add")
        flash("Book added.", "ok")
        return redirect(url_for("books"))
    return render_template("book_form.html", book={}, authors=authors_list,
                           mode="Add")


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = db.query("SELECT * FROM Book WHERE book_id = %s", (book_id,), one=True)
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("books"))
    authors_list = db.query("SELECT author_id, name FROM Author ORDER BY name")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price = parse_price(request.form.get("price", ""))
        author_id = request.form.get("author_id", "")
        if not title or price is None or not author_id.isdigit():
            flash("Title, a valid price and an author are required.", "error")
            return render_template("book_form.html", book={**book, **request.form},
                                   authors=authors_list, mode="Edit")
        cover = save_image("cover")
        try:
            if cover:
                db.execute(
                    "UPDATE Book SET title=%s, price=%s, author_id=%s, image_url=%s "
                    "WHERE book_id=%s", (title, price, int(author_id), cover, book_id))
                remove_image(book["image_url"])
            else:
                db.execute(
                    "UPDATE Book SET title=%s, price=%s, author_id=%s "
                    "WHERE book_id=%s", (title, price, int(author_id), book_id))
        except MySQLError as e:
            remove_image(cover)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("book_form.html", book={**book, **request.form},
                                   authors=authors_list, mode="Edit")
        flash("Book updated.", "ok")
        return redirect(url_for("books"))
    return render_template("book_form.html", book=book, authors=authors_list,
                           mode="Edit")


# ---------- F2.4 remove book ----------
@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.query("SELECT image_url FROM Book WHERE book_id = %s", (book_id,), one=True)
    if book:
        try:
            db.execute("DELETE FROM Book WHERE book_id = %s", (book_id,))
        except MySQLError as e:
            flash(f"Database error: {e.args[-1]}", "error")
            return redirect(url_for("books"))
        remove_image(book["image_url"])
        flash("Book removed.", "ok")
    return redirect(url_for("books"))


# ---------- F2.2 add / F2.3 edit author ----------
@app.route("/authors/add", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        if not name or not country:
            flash("Author name and country are required.", "error")
            return render_template("author_form.html", author=request.form,
                                   mode="Add")
        photo = save_image("photo")
        try:
            db.execute("INSERT INTO Author (name, country, image_url) "
                       "VALUES (%s, %s, %s)", (name, country, photo))
        except MySQLError as e:
            remove_image(photo)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("author_form.html", author=request.form,
                                   mode="Add")
        flash("Author added.", "ok")
        return redirect(url_for("authors"))
    return render_template("author_form.html", author={}, mode="Add")


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    author = db.query("SELECT * FROM Author WHERE author_id = %s", (author_id,),
                      one=True)
    if not author:
        flash("Author not found.", "error")
        return redirect(url_for("authors"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        if not name or not country:
            flash("Author name and country are required.", "error")
            return render_template("author_form.html",
                                   author={**author, **request.form}, mode="Edit")
        photo = save_image("photo")
        try:
            if photo:
                db.execute("UPDATE Author SET name=%s, country=%s, image_url=%s "
                           "WHERE author_id=%s",
                           (name, country, photo, author_id))
                remove_image(author["image_url"])
            else:
                db.execute("UPDATE Author SET name=%s, country=%s "
                           "WHERE author_id=%s", (name, country, author_id))
        except MySQLError as e:
            remove_image(photo)
            flash(f"Database error: {e.args[-1]}", "error")
            return render_template("author_form.html",
                                   author={**author, **request.form}, mode="Edit")
        flash("Author updated.", "ok")
        return redirect(url_for("authors"))
    return render_template("author_form.html", author=author, mode="Edit")


# ---------- F2.5 remove author (books are deleted by ON DELETE CASCADE) ----------
@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = db.query("SELECT image_url FROM Author WHERE author_id = %s", (author_id,),
                      one=True)
    if author:
        # collect the covers of the books that the cascade is going to delete
        covers = db.query("SELECT image_url FROM Book WHERE author_id = %s", (author_id,))
        try:
            db.execute("DELETE FROM Author WHERE author_id = %s", (author_id,))
        except MySQLError as e:
            flash(f"Database error: {e.args[-1]}", "error")
            return redirect(url_for("authors"))
        remove_image(author["image_url"])
        for c in covers:
            remove_image(c["image_url"])
        flash("Author and all of their books removed.", "ok")
    return redirect(url_for("authors"))


@app.errorhandler(413)
def too_big(_):
    flash("Image is too large (max 5 MB).", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
