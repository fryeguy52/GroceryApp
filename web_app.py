"""Mobile-friendly LAN web interface for GroceryApp.

Run with: flask --app web_app run --host 0.0.0.0 --port 8081
This first pass intentionally keeps Todoist/Trello integrations out of web requests.
"""
from __future__ import annotations

import json
import os
import re
import requests
import secrets
import shutil
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from models import RecipeCollection  # noqa: E402

RECIPE_DIR = ROOT / "recipes"
RECIPE_DIR.mkdir(parents=True, exist_ok=True)
STORE_CONFIG = SRC / "JT_Alb.txt"
DEFAULT_STORE_CONFIG = SRC / "defaultItemDepartments.txt"
DATA_DIR = Path(os.environ.get("GROCERYAPP_DATA_DIR", Path.home() / ".local" / "share" / "groceryapp")).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)
APP_DB = DATA_DIR / "groceryapp-web.sqlite3"
THEME_FILE = DATA_DIR / "web-theme.json"
DEFAULT_THEME = {"accent": "#245b49", "header": "#173f33", "background": "#f7f7f2", "panel": "#ffffff", "text": "#202820", "muted": "#68756c", "highlight": "#e68a37"}
ALLOWED_ICONS = ["🥕", "🛒", "🥦", "🍎", "🍋", "🍅", "🧄", "🥑", "🍞", "🧺", "🍽️", "🛍️"]
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


def load_theme():
    try:
        saved = json.loads(THEME_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        saved = {}
    theme = DEFAULT_THEME.copy()
    for key in DEFAULT_THEME:
        value = saved.get(key)
        if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            theme[key] = value.lower()
    icon = saved.get("icon", "🥕")
    theme["icon"] = icon if icon in ALLOWED_ICONS else "🥕"
    return theme


@app.context_processor
def inject_theme():
    return {"app_theme": load_theme(), "available_icons": ALLOWED_ICONS}


def connect_db():
    db = sqlite3.connect(APP_DB)
    db.row_factory = sqlite3.Row
    return db


@contextmanager
def db_session():
    """Commit successful operations and always close the SQLite connection."""
    db = connect_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    with db_session() as db:
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
    with db_session() as db:
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



TAG_GROUPS = [
    ("tag_food_type", "Food type", ["chicken", "turkey", "beef", "pork", "fish", "shrimp", "vegetarian"]),
    ("tag_season", "Season", ["summer", "fall", "winter", "spring"]),
    ("tag_difficulty", "Difficulty", ["easy", "medium", "hard"]),
    ("tag_cuisine", "Cuisine", ["asian", "italian", "mexican", "american", "indian", "greek", "european", "middle eastern", "mediterranean"]),
    ("tag_cooking_method", "Cooking method", ["stove", "grill", "oven", "crock pot", "instant pot", "no cooking"]),
    ("tag_meal_type", "Meal type", ["breakfast", "lunch", "dinner", "side"]),
]
TAG_GROUP_CHOICES = {field: set(choices) for field, _label, choices in TAG_GROUPS}
ALL_CATEGORY_TAGS = set().union(*TAG_GROUP_CHOICES.values())


def ingredient_rows_from_lines(lines):
    rows = []
    for line in lines:
        parts = line.split(",", 2)
        if len(parts) == 3:
            rows.append({"amount": parts[0].strip(), "unit": parts[1].strip(), "name": parts[2].strip()})
        else:
            rows.append({"amount": "", "unit": "", "name": line.strip()})
    return rows


def recipe_editor_values(recipe=None):
    values = {"name": "", "extra_tags": "", "ingredient_rows": [{"amount": "", "unit": "", "name": ""}], "instructions": ""}
    for field, _label, _choices in TAG_GROUPS:
        values[field] = ""
    if recipe is None:
        return values
    tags = [tag.strip().casefold() for tag in recipe.tags if tag not in ("recently-used", "not-recently-used")]
    for field, _label, _choices in TAG_GROUPS:
        values[field] = next((tag for tag in tags if tag in TAG_GROUP_CHOICES[field]), "")
    values.update({
        "name": recipe.name,
        "extra_tags": ", ".join(tag for tag in tags if tag not in ALL_CATEGORY_TAGS),
        "ingredient_rows": ingredient_rows_from_lines([i.original_input_string for i in recipe.ingredient_list]) or [{"amount": "", "unit": "", "name": ""}],
        "instructions": recipe.instructional_text.rstrip(),
    })
    return values


def recipe_editor_values_from_form(name, instructions, ingredient_rows):
    values = {"name": name, "extra_tags": request.form.get("extra_tags", "").strip(), "ingredient_rows": ingredient_rows, "instructions": instructions, "import_source": request.form.get("import_source", ""), "import_note": request.form.get("import_note", "")}
    for field, _label, _choices in TAG_GROUPS:
        values[field] = request.form.get(field, "").strip().casefold()
    return values



@app.route("/recipes/import", methods=["GET", "POST"])
def import_recipe():
    if request.method == "GET":
        return render_template("recipe_import.html")
    source_url = request.form.get("url", "").strip()
    try:
        from recipe_importer import validate_public_url, fetch_html, extract_recipe
        validate_public_url(source_url)
        html, final_url = fetch_html(source_url)
        values = extract_recipe(html, final_url, TAG_GROUPS, recipe_editor_values())
        # The recipe format has no separate description field. Keep the source's
        # ingredient strings at the top for reference, followed by directions and source URL.
        instructions = values.get("instructions", "").rstrip()
        source_ingredients = values.get("source_ingredients", [])
        description_parts = []
        if source_ingredients:
            description_parts.append("Ingredients as listed on source:\n" + "\n".join(f"- {item}" for item in source_ingredients))
        if instructions:
            description_parts.append(instructions)
        description_parts.append(f"Source: {final_url}")
        values["instructions"] = "\n\n".join(description_parts).strip()
    except (ValueError, requests.RequestException) as exc:
        return render_template("recipe_import.html", error=str(exc), url=source_url), 400
    return render_template(
        "recipe_edit.html", values=values, is_new=True, original_name="",
        tag_groups=TAG_GROUPS, import_review=True,
    )


@app.get("/recipes")
def recipe_manager():
    recipes = get_recipes(include_usage=False)
    return render_template("recipes.html", recipes=sorted(recipes.recipe_list, key=lambda r: r.name.lower()))


@app.route("/recipes/new", methods=["GET", "POST"])
def new_recipe():
    if request.method == "POST":
        return save_recipe_file(None)
    return render_template("recipe_edit.html", values=recipe_editor_values(), is_new=True, original_name="", tag_groups=TAG_GROUPS)


@app.route("/recipes/<path:name>/edit", methods=["GET", "POST"])
def edit_recipe(name):
    if not name or "/" in name or "\\" in name:
        abort(404)
    path = RECIPE_DIR / f"{name}.txt"
    if not path.is_file() or path.resolve().parent != RECIPE_DIR.resolve():
        abort(404)
    recipe = get_recipes(include_usage=False).get_recipe_by_name(name)
    if recipe is None:
        abort(404)
    if request.method == "POST":
        return save_recipe_file(name)
    return render_template("recipe_edit.html", values=recipe_editor_values(recipe), is_new=False, original_name=name, tag_groups=TAG_GROUPS)


def validate_recipe_fields(name, tags, ingredients, instructions, original_name=None):
    errors = []
    if not name:
        errors.append("Recipe name is required.")
    elif len(name) > 120:
        errors.append("Recipe name must be 120 characters or fewer.")
    elif name in {".", ".."} or any(c in name for c in ("/", "\\", "\0")):
        errors.append("Recipe name cannot contain slashes or be a path.")
    if not tags:
        errors.append("Add at least one tag.")
    normalized_tags = [tag.casefold() for tag in tags]
    if len(normalized_tags) != len(set(normalized_tags)):
        errors.append("Tags must be unique; remove duplicate tags.")
    required_tag_groups = [
        ({"chicken", "turkey", "beef", "pork", "fish", "shrimp", "vegetarian"}, "food type"),
        ({"summer", "fall", "winter", "spring"}, "season"),
        ({"easy", "medium", "hard"}, "difficulty"),
        ({"asian", "italian", "mexican", "american", "indian", "greek", "european", "middle eastern", "mediterranean"}, "cuisine"),
        ({"stove", "grill", "oven", "crock pot", "instant pot", "no cooking"}, "cooking method"),
        ({"breakfast", "lunch", "dinner", "side"}, "meal type"),
    ]
    for choices, label in required_tag_groups:
        if not any(tag.casefold() in choices for tag in tags):
            errors.append(f"Add a {label} tag (for example: {', '.join(sorted(choices))}).")
    if not ingredients:
        errors.append("Add at least one ingredient.")
    if not instructions.strip():
        errors.append("Recipe instructions are required.")
    for index, line in enumerate(ingredients, start=1):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            errors.append(f"Ingredient line {index} must have three comma-separated fields: amount, unit, ingredient name.")
            continue
        amount, unit, ingredient_name = parts
        if not amount or not re.fullmatch(r"(?:\d+(?:\.\d+)?|\.\d+|\d+\s*/\s*\d+|\d+\s+\d+\s*/\s*\d+|\d+(?:\.\d+)?\s*(?:to|-)\s*\d+(?:\.\d+)?)", amount, re.IGNORECASE):
            errors.append(f"Ingredient line {index} has an invalid amount '{amount}'. Use a positive number, fraction, or range.")
        else:
            try:
                if "/" in amount:
                    pieces = amount.split()
                    numeric = sum(float(part.split("/")[0]) / float(part.split("/")[1]) for part in pieces if "/" in part) + sum(float(part) for part in pieces if "/" not in part)
                elif re.search(r"to|-", amount, re.IGNORECASE):
                    numeric = float(re.split(r"\s*to\s*|\s*-\s*", amount, maxsplit=1, flags=re.IGNORECASE)[0])
                else:
                    numeric = float(amount)
                if numeric <= 0:
                    errors.append(f"Ingredient line {index} amount must be greater than zero.")
            except (ValueError, ZeroDivisionError):
                errors.append(f"Ingredient line {index} has an invalid amount '{amount}'.")
        if not ingredient_name:
            errors.append(f"Ingredient line {index} is missing the ingredient name.")
    target = RECIPE_DIR / f"{name}.txt" if name else None
    if target and target.exists() and name != original_name:
        errors.append("A recipe with that name already exists.")
    return errors


def save_recipe_file(original_name):
    name = request.form.get("name", "").strip()
    selected_tags = [request.form.get(field, "").strip().casefold() for field, _label, _choices in TAG_GROUPS]
    extra_tags = [tag.strip().casefold() for tag in request.form.get("extra_tags", "").split(",") if tag.strip()]
    tags = [tag for tag in selected_tags if tag] + extra_tags

    amounts = request.form.getlist("ingredient_amount")
    units = request.form.getlist("ingredient_unit")
    ingredient_names = request.form.getlist("ingredient_name")
    row_count = max(len(amounts), len(units), len(ingredient_names))
    ingredient_rows, ingredients = [], []
    for index in range(row_count):
        amount = amounts[index].strip() if index < len(amounts) else ""
        unit = units[index].strip() if index < len(units) else ""
        ingredient_name = ingredient_names[index].strip() if index < len(ingredient_names) else ""
        if not (amount or unit or ingredient_name):
            continue
        ingredient_rows.append({"amount": amount, "unit": unit, "name": ingredient_name})
        ingredients.append(f"{amount}, {unit}, {ingredient_name}")

    instructions = request.form.get("instructions", "").strip()
    values = recipe_editor_values_from_form(name, instructions, ingredient_rows)
    errors = validate_recipe_fields(name, tags, ingredients, instructions, original_name)
    for field, label, choices in TAG_GROUPS:
        if request.form.get(field, "").strip().casefold() not in choices:
            errors.append(f"Choose a valid {label.lower()} tag.")
    for tag in extra_tags:
        if tag in ALL_CATEGORY_TAGS:
            errors.append(f"'{tag}' belongs in its tag dropdown, not Additional tags.")
    if not errors:
        import tempfile
        from models import Recipe
        candidate_text = "\n".join(["## tags", *tags, "", "## ingredients", *ingredients, "", "## recipe", instructions, ""])
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False) as handle:
                handle.write(candidate_text)
                candidate_path = Path(handle.name)
            try:
                parsed = Recipe(candidate_path)
                errors.extend(parsed.recipe_file_errors)
            finally:
                candidate_path.unlink(missing_ok=True)
        except (OSError, ValueError) as exc:
            errors.append(f"Recipe could not be parsed: {exc}")
    if errors:
        for error in errors:
            flash(error, "warning")
        return render_template("recipe_edit.html", values=values, is_new=original_name is None,
                               original_name=original_name or "", validation_errors=errors, tag_groups=TAG_GROUPS), 400
    target = RECIPE_DIR / f"{name}.txt"
    sections = ["## tags", *tags, "", "## ingredients", *ingredients, "", "## recipe", instructions, ""]
    temporary = target.with_suffix(".txt.tmp")
    temporary.write_text("\n".join(sections), encoding="utf-8")
    temporary.replace(target)
    if original_name and original_name != name:
        (RECIPE_DIR / f"{original_name}.txt").unlink(missing_ok=True)
        with db_session() as db:
            db.execute("UPDATE menu_recipes SET recipe_name = ? WHERE recipe_name = ?", (name, original_name))
    flash(f"Recipe {'created' if original_name is None else 'saved'}: {name}.", "success")
    return redirect(url_for("recipe_manager"))


@app.post("/recipes/<path:name>/delete")
def delete_recipe(name):
    if not name or "/" in name or "\\" in name:
        abort(404)
    path = RECIPE_DIR / f"{name}.txt"
    if not path.is_file() or path.resolve().parent != RECIPE_DIR.resolve():
        abort(404)
    path.unlink()
    with db_session() as db:
        selected = db.execute("SELECT 1 FROM menu_recipes WHERE recipe_name = ?", (name,)).fetchone()
        db.execute("DELETE FROM menu_recipes WHERE recipe_name = ?", (name,))
        if selected:
            db.execute("DELETE FROM menu_recipes")
            db.execute("DELETE FROM grocery_items")
    flash(f"Deleted recipe: {name}.", "success")
    if selected:
        flash("That recipe was on the current menu, so the saved menu and shopping list were cleared to prevent stale items.", "warning")
    return redirect(url_for("recipe_manager"))


@app.get("/history")
def history():
    from timestamp_db import TimestampDB
    with TimestampDB(TIMESTAMP_DB) as db:
        usage = db.get_all_usage()
    return render_template("history.html", usage=usage)


@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        theme = DEFAULT_THEME.copy() if request.form.get("reset") == "1" else load_theme()
        if request.form.get("reset") != "1":
            for key in DEFAULT_THEME:
                value = request.form.get(key, "")
                if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
                    theme[key] = value.lower()
            icon = request.form.get("icon", "🥕")
            theme["icon"] = icon if icon in ALLOWED_ICONS else load_theme()["icon"]
        else:
            theme["icon"] = "🥕"
        temporary = THEME_FILE.with_suffix(".tmp")
        temporary.write_text(json.dumps(theme, indent=2), encoding="utf-8")
        temporary.replace(THEME_FILE)
        flash("App appearance saved." if request.form.get("reset") != "1" else "Default appearance restored.", "success")
        return redirect(url_for("config"))
    from store_config import get_item_dept_dicts_and_print_order_from_store_config_file
    _, departments, store_order = get_item_dept_dicts_and_print_order_from_store_config_file(STORE_CONFIG)
    _, default_departments, _ = get_item_dept_dicts_and_print_order_from_store_config_file(DEFAULT_STORE_CONFIG)
    todoist_settings = SRC / "todoist_settings.py"
    return render_template(
        "config.html",
        store_order=store_order,
        store_department_count=len(departments),
        default_department_count=len(default_departments),
        todoist_configured=todoist_settings.exists(),
        data_dir=DATA_DIR,
    )


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

    with db_session() as db:
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

    flash(f"Saved {len(chosen)} recipe(s) and built the review.", "success")
    return redirect(url_for("review_menu"))


@app.get("/review")
def review_menu():
    with db_session() as db:
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
    return render_template("review.html", recipes=recipes, groups=grouped, total_count=len(items))


@app.post("/submit-todoist")
def submit_to_todoist():
    with db_session() as db:
        names = [row["recipe_name"] for row in db.execute(
            "SELECT recipe_name FROM menu_recipes ORDER BY position"
        )]
        items = [row for row in db.execute(
            "SELECT department, item FROM grocery_items ORDER BY position"
        )]

    recipes = get_recipes()
    recipe_failures = []
    try:
        from todoist_functions import post_recipe_to_todoist, post_grocery_list_to_todoist
        for name in names:
            recipe = recipes.get_recipe_by_name(name)
            if recipe is None or recipe.is_grocery_staples_recipe:
                continue
            if not post_recipe_to_todoist(recipe):
                recipe_failures.append(name)

        grocery_lines = [f'{row["department"]} -- {row["item"]}' for row in items]
        grocery_ok = post_grocery_list_to_todoist(grocery_lines) if grocery_lines else False

        if recipe_failures:
            flash("Some recipe tasks could not be confirmed in Todoist: " + ", ".join(recipe_failures) + ".", "warning")
        if grocery_ok:
            flash("Grocery list sent to Todoist.", "success")
        elif grocery_lines:
            flash("Todoist did not confirm the grocery-list upload. Check todoist_settings.py and src/todoist_errors.log.", "warning")
        if not recipe_failures and any(
            (recipes.get_recipe_by_name(name) is not None and not recipes.get_recipe_by_name(name).is_grocery_staples_recipe)
            for name in names
        ):
            flash("Recipe tasks sent to Todoist's Weekly Menu section.", "success")
    except Exception:
        app.logger.exception("Unexpected error while submitting menu to Todoist")
        flash("The menu was kept locally, but the Todoist submission failed. Check the server log.", "warning")

    return redirect(url_for("shopping_list"))


@app.get("/list")
def shopping_list():
    with db_session() as db:
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
    with db_session() as db:
        row = db.execute("SELECT checked FROM grocery_items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            abort(404)
        db.execute("UPDATE grocery_items SET checked = ? WHERE id = ?", (0 if row["checked"] else 1, item_id))
    return redirect(url_for("shopping_list"))


@app.post("/list/reset")
def reset_checks():
    with db_session() as db:
        db.execute("UPDATE grocery_items SET checked = 0")
    flash("All shopping-list items are unchecked.", "success")
    return redirect(url_for("shopping_list"))


@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", title="Please reload", message=error.description), 400


if __name__ == "__main__":
    # Flask's built-in server is for first-run testing on the trusted home LAN.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8081")), debug=False)
