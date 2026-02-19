"""
grocery_functions.py
--------------------
Top-level orchestrator. Coordinates models, GUI, store config,
and external integrations.

This module is now much thinner — data classes live in models.py,
store parsing lives in store_config.py, and the GUI no longer
imports back into this module (circular import removed).
"""

__author__ = 'Joe'

from pathlib import Path

from models import RecipeCollection
from store_config import get_all_ingredients, update_default_ing_dept_file


def run_trello_grocery_list_app(
    recipe_directory,
    grocery_store_config_file,
    default_store_file_name,
    recipe_time_stamp_file_name,
    grocery_list_output_file_name,
    post_to_trello: bool = False,
    post_to_todoist: bool = False,
    append_time_stamps: bool = True,
):
    """
    Main application entry point.

    1. Refresh the default ingredient-to-department mapping.
    2. Validate all recipe files; abort with errors if any are found.
    3. Launch the GUI so the user picks this week's recipes.
    4. Build the grocery list, optionally post to Trello/Todoist.
    5. Write the store-ordered grocery list to a file.
    6. Optionally record usage timestamps in the SQLite database.
    """
    recipe_dir = Path(recipe_directory)
    store_config = Path(grocery_store_config_file)
    default_store = Path(default_store_file_name)
    ts_file = Path(recipe_time_stamp_file_name)
    output_file = Path(grocery_list_output_file_name)

    # Step 1 — keep the default dept file up to date
    update_default_ing_dept_file(
        get_all_ingredients(recipe_dir, default_store),
        default_store,
    )

    # Step 2 — validate all recipes
    all_recipes = RecipeCollection()
    all_recipes.add_all_recipes_in_dir(recipe_dir)
    errors = all_recipes.get_recipe_file_format_errors()
    if errors:
        for err in errors:
            print(err)
        return

    # Step 3 — load timestamps, then launch GUI
    # FIX: RecipeCollection is built here and *passed into* the GUI,
    # eliminating the circular import (gui -> grocery_functions -> gui).
    all_recipes.read_time_stamp_file(ts_file)

    selected_recipes = []
    from grocery_gui import recipeGUI
    gui_post_to_todoist = recipeGUI(selected_recipes, all_recipes)

    # post_to_todoist can be overridden by the GUI checkbox;
    # if the caller passed post_to_todoist=False we always respect that.
    effective_post_to_todoist = post_to_todoist and gui_post_to_todoist

    # Step 4 — build the weekly collection
    recipes_for_the_week = RecipeCollection()
    for recipe_name in selected_recipes:
        recipe = all_recipes.get_recipe_by_name(recipe_name)
        if recipe is None:
            continue
        recipes_for_the_week.add_recipe(recipe)

        if post_to_trello and not recipe.is_grocery_staples_recipe:
            from trello_functions import post_recipe_to_trello
            post_recipe_to_trello(recipe)

        if effective_post_to_todoist and not recipe.is_grocery_staples_recipe:
            from todoist_functions import post_recipe_to_todoist
            post_recipe_to_todoist(recipe)

    # Step 5 — build + write grocery list
    recipes_for_the_week.sort_grocery_list_by_store_order(store_config, default_store)
    recipes_for_the_week.write_store_ordered_grocery_list_to_file(output_file)

    # Step 5b — post grocery list to Todoist as a parent task with subtasks
    if effective_post_to_todoist:
        from todoist_functions import post_grocery_list_to_todoist
        post_grocery_list_to_todoist(recipes_for_the_week.grocery_list_by_store_order)

    # Step 6 — record usage
    if append_time_stamps:
        recipes_for_the_week.write_recipe_usage_data(ts_file)
