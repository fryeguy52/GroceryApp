"""Website recipe extraction helpers for GroceryApp."""
import ipaddress
import json
import re
import socket
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


def validate_public_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Enter a full public http:// or https:// recipe URL.")
    host = parsed.hostname.rstrip(".").casefold()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Local network addresses cannot be imported.")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)]
        except (OSError, ValueError):
            raise ValueError("The website address could not be resolved.")
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("The URL must point to a public website, not a private or local address.")
    return parsed


def fetch_html(url):
    current = url
    for _ in range(4):
        validate_public_url(current)
        response = requests.get(
            current, timeout=(4, 8), allow_redirects=False, stream=True,
            headers={"User-Agent": "GroceryAppRecipeImporter/1.0"},
        )
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise ValueError("The website redirected without a destination.")
            current = urljoin(current, location)
            continue
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if content_type and not ("text/html" in content_type or "application/xhtml+xml" in content_type):
            response.close()
            raise ValueError("That URL did not return an HTML recipe page.")
        chunks, size = [], 0
        try:
            for chunk in response.iter_content(chunk_size=16384):
                if not chunk:
                    continue
                size += len(chunk)
                if size > 2_000_000:
                    raise ValueError("The recipe page is too large to import (2 MB limit).")
                chunks.append(chunk)
        finally:
            response.close()
        return b"".join(chunks), current
    raise ValueError("The website redirected too many times.")


def _is_recipe_type(value):
    values = value if isinstance(value, list) else [value]
    return any(str(item).rsplit("/", 1)[-1].rsplit("#", 1)[-1] == "Recipe" for item in values)


def _find_recipes(value):
    found = []
    if isinstance(value, dict):
        if _is_recipe_type(value.get("@type")):
            found.append(value)
        for child in value.values():
            found.extend(_find_recipes(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_recipes(child))
    return found


def _text(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(value.get("name") or value.get("text") or value.get("url") or "").strip()
    if isinstance(value, list):
        return ", ".join(filter(None, (_text(item) for item in value)))
    return ""


def _instructions(value):
    lines = []
    def visit(item):
        if isinstance(item, str):
            if item.strip():
                lines.append(item.strip())
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            if item.get("@type") == "HowToSection":
                title = _text(item.get("name"))
                if title:
                    lines.append(title + ":")
                visit(item.get("itemListElement", []))
            elif item.get("text"):
                visit(item["text"])
            elif item.get("itemListElement"):
                visit(item["itemListElement"])
    visit(value)
    return "\n".join(lines)


def _ingredient_fields(raw):
    text = str(raw).strip().lstrip("•*- ").strip()
    quantity = r"(?:\d+\s+\d+\s*/\s*\d+|\d+\s*/\s*\d+|\d+(?:\.\d+)?|[½¼¾⅓⅔⅛⅜⅝⅞])"
    match = re.match(rf"^({quantity}(?:\s*(?:-|–|to)\s*{quantity})?)(?:\s+|$)(.*)$", text, re.IGNORECASE)
    if not match:
        return {"amount": "", "unit": "", "name": text}
    amount, remainder = match.group(1).strip(), match.group(2).strip()
    unit_match = re.match(
        r"^(cups?|c|tablespoons?|tbsp|tbsps|teaspoons?|tsp|tsps|ounces?|oz|pounds?|lbs?|grams?|g|kilograms?|kg|milliliters?|ml|liters?|l|cloves?|cans?|packages?|pkg|bags?|boxes|large|medium|small|pinches?|slices?|pieces?)\b\s*(.*)$",
        remainder, re.IGNORECASE,
    )
    if unit_match:
        return {"amount": amount, "unit": unit_match.group(1).strip(), "name": unit_match.group(2).strip()}
    return {"amount": amount, "unit": "", "name": remainder}


def extract_recipe(html, source_url, tag_groups, base_values):
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for script in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        try:
            candidates.extend(_find_recipes(json.loads(script.string or script.get_text())))
        except (json.JSONDecodeError, TypeError):
            continue
    if not candidates:
        raise ValueError("No Schema.org Recipe data was found on that page. Try another recipe URL or add it manually.")
    recipe = max(candidates, key=lambda item: bool(item.get("recipeIngredient")) and bool(item.get("recipeInstructions")))
    name = _text(recipe.get("name")) or (soup.title.get_text(" ", strip=True) if soup.title else "")
    raw_ingredients = recipe.get("recipeIngredient", [])
    if isinstance(raw_ingredients, str):
        raw_ingredients = [raw_ingredients]
    ingredient_rows = [_ingredient_fields(_text(item)) for item in raw_ingredients if _text(item)]
    instructions = _instructions(recipe.get("recipeInstructions", []))
    if not name or not ingredient_rows or not instructions:
        raise ValueError("Recipe data was found, but the page did not provide a name, ingredients, and instructions.")
    values = dict(base_values)
    values.update({
        "name": name[:120], "ingredient_rows": ingredient_rows, "instructions": instructions,
        "import_source": source_url,
        "import_note": "Imported fields are a best-effort conversion. Review every ingredient and choose the correct tags before saving.",
    })
    cuisine = _text(recipe.get("recipeCuisine")).casefold()
    category = _text(recipe.get("recipeCategory")).casefold()
    method = _text(recipe.get("cookingMethod")).casefold()
    method = {"baking": "oven", "roasting": "oven", "frying": "stove", "slow cooker": "crock pot"}.get(method, method)
    for field, _label, choices in tag_groups:
        if field == "tag_cuisine" and cuisine in choices:
            values[field] = cuisine
        elif field == "tag_meal_type" and category in choices:
            values[field] = category
        elif field == "tag_cooking_method" and method in choices:
            values[field] = method
    combined = (name + " " + " ".join(_text(item) for item in raw_ingredients)).casefold()
    for tag, keywords in [
        ("chicken", ["chicken"]), ("turkey", ["turkey"]), ("beef", ["beef", "steak"]),
        ("pork", ["pork", "bacon", "ham", "sausage"]), ("fish", ["salmon", "tuna", "cod", "tilapia", "fish"]),
        ("shrimp", ["shrimp", "prawn"]),
    ]:
        if any(re.search(r"\b" + re.escape(word) + r"\b", combined) for word in keywords):
            values["tag_food_type"] = tag
            break
    return values
