"""
main.py
Entry point for the GroceryApp.
"""
__author__ = 'Joe'

from pathlib import Path
import grocery_functions

if __name__ == "__main__":
    # All paths are relative to this file's location so the app runs from any
    # working directory (pathlib replaces the old hardcoded Windows backslashes).
    _ROOT = Path(__file__).parent.parent

    grocery_functions.run_trello_grocery_list_app(
        recipe_directory              = _ROOT / "recipes",
        grocery_store_config_file     = Path(__file__).parent / "JT_Alb.txt",
        default_store_file_name       = Path(__file__).parent / "defaultItemDepartments.txt",
        recipe_time_stamp_file_name   = _ROOT / "recipe_time_stamps.db",
        grocery_list_output_file_name = _ROOT / "most_recent_grocery_list.txt",
        post_to_trello    = False,
        post_to_todoist   = True,
        append_time_stamps = True,
    )
