"""
grocery_functions.py
Orchestrator: wires together models, store config, GUI, and integrations.

This module is now intentionally thin — all business logic lives in:
  models.py        — Ingredient, Recipe, RecipeCollection
  store_config.py  — department file parsing / updating
  timestamp_db.py  — SQLite-backed usage history
  grocery_gui.py   — appJar GUI
  trello_functions.py  / todoist_functions.py — external integrations
"""
__author__ = 'Joe'

import datetime
from pathlib import Path

from models       import RecipeCollection
from store_config import get_all_ingredients, update_default_ing_dept_file
import grocery_gui
import trello_functions
import todoist_functions


def run_trello_grocery_list_app(
    recipe_directory:              str | Path,
    grocery_store_config_file:     str | Path,
    default_store_file_name:       str | Path,
    recipe_time_stamp_file_name:   str | Path,
    grocery_list_output_file_name: str | Path,
    post_to_trello:   bool = False,
    post_to_todoist:  bool = False,
    append_time_stamps: bool = True,
) -> None:
    """
    Main application entry point.

    1. Refresh the default ingredient→department file.
    2. Load and validate all recipes.
    3. If no format errors: show the GUI, build the grocery list, post to
       Trello / Todoist if enabled, write output file, record timestamps.
    4. If format errors exist: print them and exit without showing the GUI.
    """

    recipe_directory            = Path(recipe_directory)
    grocery_store_config_file   = Path(grocery_store_config_file)
    default_store_file_name     = Path(default_store_file_name)
    recipe_time_stamp_file_name = Path(recipe_time_stamp_file_name)
    grocery_list_output_file_name = Path(grocery_list_output_file_name)

    # Step 1 — keep the default department file in sync with the recipe corpus
    update_default_ing_dept_file(
        get_all_ingredients(recipe_directory, default_store_file_name),
        default_store_file_name,
    )

    # Step 2 — load all recipes and check for format errors
    all_recipes = RecipeCollection()
    all_recipes.add_all_recipes_in_dir(recipe_directory)

    errors = all_recipes.get_recipe_file_format_errors()
    if errors:
        for error in errors:
            print(error)
        return

    # Step 3 — show GUI; user picks recipes for the week
    selected_recipes: list[str] = []
    recipe_collection_with_timestamps = RecipeCollection()
    recipe_collection_with_timestamps.add_all_recipes_in_dir(recipe_directory)
    recipe_collection_with_timestamps.read_time_stamp_file(recipe_time_stamp_file_name)

    # Pass the pre-loaded collection into the GUI (no circular import)
    grocery_gui.recipeGUI(selected_recipes, recipe_collection_with_timestamps)

    # Step 4 — assemble the week's grocery list
    recipes_for_the_week = RecipeCollection()
    for recipe_name in selected_recipes:
        recipe = all_recipes.get_recipe_by_name(recipe_name)
        if recipe is None:
            continue
        recipes_for_the_week.add_recipe(recipe)

        if post_to_trello and not recipe.is_grocery_staples_recipe:
            trello_functions.post_recipe_to_trello(recipe)
        if post_to_todoist and not recipe.is_grocery_staples_recipe:
            todoist_functions.post_recipe_to_todoist(recipe)

    recipes_for_the_week.get_grocery_list_by_store_order(
        grocery_store_config_file, default_store_file_name
    )
    recipes_for_the_week.write_store_ordered_grocery_list_to_file(
        grocery_list_output_file_name
    )

    if append_time_stamps:
        recipes_for_the_week.write_recipe_usage_data(recipe_time_stamp_file_name)
