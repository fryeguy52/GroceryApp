"""
store_config.py
---------------
Parsing and updating store/department configuration files.
Extracted from grocery_functions.py. Uses pathlib for cross-platform paths.
"""

__author__ = 'Joe'

from pathlib import Path


def get_item_dept_dicts_and_print_order_from_store_config_file(file_name):
    """
    Parse a store config file and return:
      - ingredient_dept_dict  : {ingredient_name -> department}
      - dept_list_of_ing_dict : {department -> [ingredient_names]}
      - print_order_list      : [department, ...] in aisle traversal order
    """
    heading = ''
    dept_list_of_ing_dict = {}
    ingredient_dept_dict  = {}
    print_order_list      = []

    with open(Path(file_name), 'r') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                heading = stripped.lstrip('#').strip().lower()
                if heading != 'print order':
                    dept_list_of_ing_dict[heading] = []
            elif heading == 'print order':
                print_order_list.append(stripped.lower())
            else:
                dept_list_of_ing_dict.setdefault(heading, []).append(stripped)
                ingredient_dept_dict[stripped] = heading

    return ingredient_dept_dict, dept_list_of_ing_dict, print_order_list


def get_all_ingredients_from_store_config_file(file_name):
    """Return a flat list of all ingredient names in a store config file."""
    heading = ''
    all_ingredients = []
    with open(Path(file_name), 'r') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                heading = stripped.lstrip('#').strip().lower()
            elif heading != 'print order':
                all_ingredients.append(stripped)
    return all_ingredients


def get_all_ingredients(recipe_dir, default_item_dept_file_name):
    """
    Sorted, deduplicated list of every ingredient found across all recipes
    plus every item already in the default dept config file.
    """
    from models import RecipeCollection
    all_recipes = RecipeCollection()
    all_recipes.add_all_recipes_in_dir(recipe_dir)
    ingredient_set = set(all_recipes.get_unique_ingredient_list())
    ingredient_set.update(get_all_ingredients_from_store_config_file(default_item_dept_file_name))
    return sorted(ingredient_set)


def update_default_ing_dept_file(input_list, default_store_file_name):
    """
    Rewrite the default store config file preserving existing dept assignments.
    Unassigned ingredients are appended at the end.
    """
    path = Path(default_store_file_name)
    default_dept_from_ing, _, print_order = \
        get_item_dept_dicts_and_print_order_from_store_config_file(path)

    print_order_sorted = sorted(print_order)

    with open(path, 'w') as f:
        f.write('## print order\n')
        for dept in print_order_sorted:
            f.write(dept + '\n')
        for dept in print_order_sorted:
            f.write(f'\n## {dept}\n')
            for item in input_list:
                if default_dept_from_ing.get(item) == dept:
                    f.write(item + '\n')
        for item in input_list:
            if item not in default_dept_from_ing:
                f.write(item + '\n')
