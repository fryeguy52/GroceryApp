"""Mobile-friendly LAN web interface for GroceryApp.

Run with: flask --app web_app run --host 0.0.0.0 --port 8081
This first pass intentionally keeps Todoist/Trello integrations out of web requests.
"""
from __future__ import annotations

import os
import secrets
import shutil
import sqlite3
import sys
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from models import RecipeCollection  # noqa: E402

RECIPE_DIR = ROOT / "recipes"
STORE_CONFIG = SRC / "JT_Alb.txt"
DEFAULT_STORE_CONFIG = SRC / "defaultItemDepartments.txt"
DATA_DIR = Path(os.environ.get("GROCERYAPP_DATA_DIR", Path.home() / ".local" / "share" / "groceryapp")).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)
APP_DB = DATA_DIR / "groceryapp-web.sqlite3"
TIMESTAMP_DB = DATA_DIR / "recipe_time_stamps.db"
LEGACY_TIMESTAMP_DB = ROOT / "recipe_time_stamps.db"

# Preserve the existing usage history on first run, but keep future writes out of the git checkout.
if not TIMESTAMP_DB.exists() and LEGACY_TIMESTAMP_DB.exists():
    shutil.copy2(LEGACY_TIMESTAMP_DB, TIMESTAMP_DB)

_secret_file = DATA_DIR / "flask-secret"
if not _secret_file.exists():
    _secret_file.write_text(secrets.token_hex(32), encoding="utf-8")
app = Flask(__name__)
app.secret_key = os.environ.get("GROCERYAPP_SECRET_KEY", _secret_file.read_text(encoding="utf-8").strip())
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def connect_db():
    db = sqlite3.connect(APP_DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS menu_recipes (
                position INTEGER PRIMARY KEY,
                recipe_name TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS grocery_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position INTEGER NOT NULL,
                department TEXT NOT NULL,
                item TEXT NOT NULL,
                checked INTEGER NOT NULL DEFAULT 0
            )
        """)


init_db()


def get_recipes(*, include_usage=True):
    recipes = RecipeCollection()
    recipes.add_all_recipes_in_dir(RECIPE_DIR)
    if include_usage:
        recipes.read_time_stamp_file(TIMESTAMP_DB)
    return recipes


def csrf_token():
    token = session.get("_csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def protect_post_requests():
    if request.method == "POST":
        submitted = request.form.get("_csrf_token", "")
        expected = session.get("_csrf_token", "")
        if not submitted or not expected or not secrets.compare_digest(submitted, expected):
            abort(400, description="The form expired or could not be verified. Reload the page and try again.")


@app.get("/")
def index():
    tags = request.args.get("tags", "").strip().lower().split()
    recipes = get_recipes()
    names = recipes.get_recipe_names(tags)
    if names and names[0].startswith("No recipes match"):
        names = []
        no_matches = True
    else:
        no_matches = False
    with connect_db() as db:
        selected = [row["recipe_name"] for row in db.execute(
            "SELECT recipe_name FROM menu_recipes ORDER BY position"
        )]
    return render_template(
        "index.html", recipes=recipes.recipe_list, names=set(names),
        tags=" ".join(tags), selected=selected, no_matches=no_matches,
    )


@app.get("/recipe/<path:name>")
def recipe_detail(name):
    recipe = get_recipes().get_recipe_by_name(name)
    if recipe is None:
        abort(404)
    return render_template("recipe.html", recipe=recipe)


@app.post("/menu")
def save_menu():
    names = request.form.getlist("recipe")
    recipes = get_recipes()
    valid_names = set(recipes.get_recipe_names([]))
    # Preserve order while removing duplicate selections and rejecting unknown names.
    chosen = list(dict.fromkeys(name for name in names if name in valid_names))
    selected_collection = RecipeCollection()
    for name in chosen:
        recipe = recipes.get_recipe_by_name(name)
        if recipe:
            selected_collection.add_recipe(recipe)

    selected_collection.sort_grocery_list_by_store_order(STORE_CONFIG, DEFAULT_STORE_CONFIG)
    selected_collection.write_recipe_usage_data(TIMESTAMP_DB)

    with connect_db() as db:
        db.execute("DELETE FROM menu_recipes")
        db.execute("DELETE FROM grocery_items")
        db.executemany(
            "INSERT INTO menu_recipes(position, recipe_name) VALUES (?, ?)",
            [(i, name) for i, name in enumerate(chosen)],
        )
        rows = []
        for i, line in enumerate(selected_collection.grocery_list_by_store_order):
            if " -- " in line:
                department, item = line.split(" -- ", 1)
            else:
                department, item = "No Department Listed", line
            rows.append((i, department, item))
        db.executemany(
            "INSERT INTO grocery_items(position, department, item) VALUES (?, ?, ?)", rows
        )
    flash(f"Saved {len(chosen)} recipe(s) and rebuilt the shopping list.", "success")
    return redirect(url_for("shopping_list"))


@app.get("/list")
def shopping_list():
    with connect_db() as db:
        recipes = [row["recipe_name"] for row in db.execute(
            "SELECT recipe_name FROM menu_recipes ORDER BY position"
        )]
        items = [dict(row) for row in db.execute(
            "SELECT id, position, department, item, checked FROM grocery_items ORDER BY position"
        )]
    grouped = []
    for item in items:
        if not grouped or grouped[-1]["department"] != item["department"]:
            grouped.append({"department": item["department"], "items": []})
        grouped[-1]["items"].append(item)
    checked_count = sum(item["checked"] for item in items)
    return render_template(
        "list.html", recipes=recipes, groups=grouped,
        checked_count=checked_count, total_count=len(items),
    )


@app.post("/list/check/<int:item_id>")
def toggle_item(item_id):
    with connect_db() as db:
        row = db.execute("SELECT checked FROM grocery_items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            abort(404)
        db.execute("UPDATE grocery_items SET checked = ? WHERE id = ?", (0 if row["checked"] else 1, item_id))
    return redirect(url_for("shopping_list"))


@app.post("/list/reset")
def reset_checks():
    with connect_db() as db:
        db.execute("UPDATE grocery_items SET checked = 0")
    flash("All shopping-list items are unchecked.", "success")
    return redirect(url_for("shopping_list"))


@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", title="Please reload", message=error.description), 400


if __name__ == "__main__":
    # Flask's built-in server is for first-run testing on the trusted home LAN.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8081")), debug=False)
