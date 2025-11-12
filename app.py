"""A simple Flask application to manage text notes:
- List existing notes"""

import os
import time

from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    redirect,
    url_for,
)


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"


def allow_file(filename):
    """Дозволити лише текстові файли"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"txt"}


def get_file_list():
    """Отримати список файлів нотаток"""
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if allow_file(filename):
            files.append(filename)
    return files


@app.route("/")
def home():
    """Головна сторінка - список нотаток"""
    files = get_file_list()
    return render_template("file_list.html", files=files)


@app.route("/uploads/<path:filename>")
def download_file(filename):
    """Завантаження файлу нотатки"""
    return send_from_directory("uploads", filename, as_attachment=True)


@app.route("/create_note", methods=["GET", "POST"])
def create_note():
    """Створення нової нотатки"""

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        if title and content:
            new_note = {"id": time.time(), "title": title, "content": content}

            filename = (
                f"{int(new_note['id'])}_{new_note['title'].replace(' ', '_')}.txt"
            )
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_note["content"])

            return redirect(url_for("home"))

    return render_template("create_note.html", note=None)


@app.route("/update_note/<filename>", methods=["GET", "POST"])
def update_note(filename):
    """Редагування існуючої нотатки"""
    # Знайти нотатку за ім'ям файлу
    filepath = os.path.join(UPLOAD_FOLDER, filename) + ".txt"
    print(f"Шлях до файлу: {filepath}")
    if not os.path.exists(filepath):
        return "Нотатку не знайдено", 404

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        content = content.replace("line", "\n_____\n")  # Нормалізація нових рядків

        if title and content:

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return redirect(url_for("home"))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return render_template(
        "create_note.html", note={"title": filename, "content": content}
    )


if __name__ == "__main__":

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, host="0.0.0.0", port=5000)
