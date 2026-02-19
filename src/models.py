"""
models.py
---------
Core data model classes: Ingredient, Recipe, RecipeCollection.
"""

__author__ = 'Joe'

import datetime
import sqlite3
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Unit normalization
# ---------------------------------------------------------------------------

_UNIT_ALIASES = {
    # tablespoons -> canonical 'tbsp'
    'tablespoon': 'tbsp', 'tablespoons': 'tbsp',
    'tbsp': 'tbsp', 'tbsps': 'tbsp', 'tbs': 'tbsp',
    # teaspoons -> canonical 'tsp'
    'teaspoon': 'tsp', 'teaspoons': 'tsp',
    'tsp': 'tsp', 'tsps': 'tsp',
    # cups
    'cup': 'cup', 'cups': 'cup', 'c': 'cup',
    # ounces
    'ounce': 'oz', 'ounces': 'oz', 'oz': 'oz',
    # pounds
    'pound': 'lb', 'pounds': 'lb', 'lb': 'lb', 'lbs': 'lb',
    # containers (non-convertible, kept as-is)
    'can': 'can', 'cans': 'can',
    'package': 'package', 'packages': 'package', 'pkg': 'package',
    'dozen': 'dozen', 'gallon': 'gallon',
    'clove': 'clove', 'cloves': 'clove',
    'jar': 'jar', 'jars': 'jar',
    'bag': 'bag', 'bags': 'bag',
    'box': 'box', 'boxes': 'box',
    'carton': 'carton', 'container': 'container',
    'medium': 'medium', 'large': 'large', 'small': 'small',
}

# tablespoon as base volume unit; lb as base weight unit
_TO_TBSP = {'tbsp': 1.0, 'tsp': 1 / 3.0, 'cup': 16.0}
_TO_LB   = {'lb': 1.0, 'oz': 1 / 16.0}


def _normalize_unit(raw: str) -> str:
    """Map a raw unit string to its canonical form. Looks up exact match first, then strips trailing 's' for plurals."""
    key = raw.strip().lower()
    if key in _UNIT_ALIASES:
        return _UNIT_ALIASES[key]
    # Try de-pluralizing
    stripped = key.rstrip('s').rstrip('.')
    return _UNIT_ALIASES.get(stripped, key)


def _try_combine(amount1: float, unit1: str, amount2: float, unit2: str):
    """Return (combined_amount, unit) if units are compatible, else None."""
    u1, u2 = _normalize_unit(unit1), _normalize_unit(unit2)
    if u1 == u2:
        return amount1 + amount2, u1
    if u1 in _TO_TBSP and u2 in _TO_TBSP:
        total = amount1 * _TO_TBSP[u1] + amount2 * _TO_TBSP[u2]
        for unit, factor in sorted(_TO_TBSP.items(), key=lambda x: -x[1]):
            if total / factor >= 0.25:
                return round(total / factor, 3), unit
    if u1 in _TO_LB and u2 in _TO_LB:
        return round(amount1 * _TO_LB[u1] + amount2 * _TO_LB[u2], 3), 'lb'
    return None


# ---------------------------------------------------------------------------
# Ingredient
# ---------------------------------------------------------------------------

class Ingredient:
    """
    Parsed from a recipe line in "number, unit, name" CSV format.
    """
    def __init__(self, input_string: str):
        self.original_input_string = input_string
        self.format_error = ''
        self.recipe_name = ''

        parts = input_string.split(',')
        if len(parts) == 3:
            self.number = parts[0].strip().lower().rstrip('s.')
            self.unit   = _normalize_unit(parts[1])
            self.name   = parts[2].strip().lower().rstrip('s.')
            if self.name.endswith('oe'):
                self.name = self.name.rstrip('e')
        else:
            self.format_error = 'invalid input line: ' + input_string
            self.name = self.unit = self.number = self.format_error

    def get_name(self)   -> str: return self.name
    def get_unit(self)   -> str: return self.unit
    def get_number(self) -> str: return self.number


# ---------------------------------------------------------------------------
# Recipe
# ---------------------------------------------------------------------------

class Recipe:
    """
    Loaded from a structured text file with ## tags, ## ingredients, ## recipe sections.
    """

    ACCEPTABLE_HEADINGS = {'tags', 'ingredients', 'recipe'}

    REQUIRED_TAG_SETS = [
        ['chicken', 'turkey', 'beef', 'pork', 'fish', 'shrimp', 'vegetarian'],
        ['summer', 'fall', 'winter', 'spring'],
        ['easy', 'medium', 'hard'],
        ['asian', 'italian', 'mexican', 'american', 'indian', 'greek',
         'european', 'middle eastern', 'mediterranean'],
        ['stove', 'grill', 'oven', 'crock pot', 'instant pot', 'no cooking'],
        ['breakfast', 'lunch', 'dinner', 'side'],
    ]

    def __init__(self, recipe_file_path):
        path = Path(recipe_file_path)
        self.file_name = path
        self.name = path.stem  # cross-platform: no os.sep needed

        self.instructional_text = ''
        self.ingredient_list: list = []
        self.recipe_file_errors: list = []
        self.tags: list = []
        self.list_of_ingredient_names: list = []
        self.is_selected = False
        self.is_grocery_staples_recipe = 'Grocery Staples' in path.name
        self.distance_to_recipe_dict: dict = {}
        self.average_distance: float = 0.0

        heading = ''
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                if line.startswith('#'):
                    candidate = line.lstrip('#').strip().lower()
                    if candidate in self.ACCEPTABLE_HEADINGS:
                        heading = candidate
                    else:
                        self.recipe_file_errors.append(f'{candidate} is not a valid heading')
                elif heading == 'ingredients':
                    ing = Ingredient(line.rstrip('\n'))
                    ing.recipe_name = self.name
                    self.list_of_ingredient_names.append(ing.name)
                    self.ingredient_list.append(ing)
                    if ing.format_error:
                        self.recipe_file_errors.append(ing.format_error)
                elif heading == 'recipe':
                    self.instructional_text += line
                elif heading == 'tags':
                    self.tags.append(line.strip())

        self._check_for_missing_tags()
        self._sort_ingredient_list()

    def get_name(self)               -> str:  return self.name
    def get_instructional_text(self) -> str:  return self.instructional_text
    def get_ingredient_list(self)    -> list: return self.ingredient_list

    def add_ingredient(self, ing):
        self.ingredient_list.append(ing)
        self._sort_ingredient_list()

    def add_tag(self, tag: str):
        self.tags.append(tag)

    def calculate_distance_from_another_recipe(self, other: 'Recipe') -> float:
        """
        BUG FIX: original used self.tags for both recipes when computing tag
        overlap — tag distance was always 0. Now correctly uses other.tags.
        """
        common_ing  = set(self.list_of_ingredient_names) & set(other.list_of_ingredient_names)
        diff_ing    = set(self.list_of_ingredient_names) ^ set(other.list_of_ingredient_names)
        common_tags = set(self.tags) & set(other.tags)          # fixed
        diff_tags   = set(self.tags) ^ set(other.tags)          # fixed

        total_common = len(common_ing) + len(common_tags)
        total_all    = total_common + len(diff_ing) + len(diff_tags)

        pct = float(total_common / total_all) if total_all else 0.0
        self.distance_to_recipe_dict[other.name] = round(1 - pct, 4)
        self._recalculate_average_distance()
        return pct

    def _sort_ingredient_list(self):
        self.ingredient_list.sort(key=lambda x: x.name)

    def _check_for_missing_tags(self):
        for tag_set in self.REQUIRED_TAG_SETS:
            if not any(t in self.tags for t in tag_set):
                self.recipe_file_errors.append('Missing one of the following tags: ' + str(tag_set))

    def _recalculate_average_distance(self):
        d = self.distance_to_recipe_dict
        self.average_distance = sum(d.values()) / len(d) if d else 0.0


# ---------------------------------------------------------------------------
# RecipeCollection
# ---------------------------------------------------------------------------

class RecipeCollection:
    """
    A collection of Recipe objects. Handles grocery list generation (with unit
    normalization), store-order sorting, tag-based filtering, recipe distance
    calculation, and SQLite-backed usage tracking.
    """

    def __init__(self):
        self.recipe_list:                list = []
        self.grocery_list:               list = []
        self.grocery_list_by_store_order: list = []
        self.recipe_file_format_errors:  list = []
        self.unique_ingredient_list:     list = []
        self.ingredient_count_dict:      dict = {}

    # -- Building ----------------------------------------------------------

    def add_recipe(self, recipe: Recipe):
        self.recipe_list.append(recipe)

    def add_all_recipes_in_dir(self, recipe_dir):
        for file in sorted(Path(recipe_dir).glob('*.txt')):
            self.recipe_list.append(Recipe(file))

    # -- Querying ----------------------------------------------------------

    def get_recipe_by_name(self, name: str):
        for r in self.recipe_list:
            if r.get_name() == name:
                return r
        print(f'{name} Not Found!')
        return None

    def get_recipe_names(self, search_tags: list = []) -> list:
        if not search_tags:
            return [r.name for r in self.recipe_list]
        matches = [r.name for r in self.recipe_list if set(search_tags).issubset(r.tags)]
        return matches if matches else [f'No recipes match the tags: {search_tags}']

    def get_recipe_file_format_errors(self) -> list:
        self.recipe_file_format_errors = [
            f'{r.name}: {err}' for r in self.recipe_list for err in r.recipe_file_errors
        ]
        return self.recipe_file_format_errors

    def get_unique_ingredient_list(self) -> list:
        seen = set()
        self.unique_ingredient_list = []
        for r in self.recipe_list:
            for ing in r.ingredient_list:
                if ing.name not in seen:
                    seen.add(ing.name)
                    self.unique_ingredient_list.append(ing.name)
        self.unique_ingredient_list.sort()
        return self.unique_ingredient_list

    def get_grocery_list(self) -> list:
        self.make_ingredient_list()
        return self.grocery_list

    def get_grocery_list_by_store_order(self, store_config_file, default_store_file) -> list:
        self.sort_grocery_list_by_store_order(store_config_file, default_store_file)
        return self.grocery_list_by_store_order

    # -- Grocery list (unit normalization fix) -----------------------------

    def make_ingredient_list(self):
        """
        Aggregate ingredients across all recipes.

        FIX: same ingredient in different units (e.g. "3 tbsp olive oil" and
        "1 cup olive oil") is now converted to a common unit instead of
        emitting the garbled "7.5 tablespoon, 1 " output.
        """
        name_entries: dict = defaultdict(list)
        for recipe in self.recipe_list:
            for ing in recipe.get_ingredient_list():
                try:
                    amount = float(ing.number)
                except (ValueError, TypeError):
                    amount = 1.0
                name_entries[ing.name].append((amount, ing.unit))

        self.grocery_list = []
        for name in sorted(name_entries):
            combined: list = []
            for amount, unit in name_entries[name]:
                merged = False
                for i, (c_amt, c_unit) in enumerate(combined):
                    result = _try_combine(c_amt, c_unit, amount, unit)
                    if result is not None:
                        combined[i] = result
                        merged = True
                        break
                if not merged:
                    combined.append((amount, unit))
            parts = ', '.join(f'{amt:g} {u}'.strip() for amt, u in combined)
            self.grocery_list.append(f'{name}: {parts}')

    def sort_grocery_list_by_store_order(self, store_config_file, default_store_file):
        from store_config import get_item_dept_dicts_and_print_order_from_store_config_file
        self.make_ingredient_list()
        self.grocery_list_by_store_order = []

        store_dept, _, store_order = get_item_dept_dicts_and_print_order_from_store_config_file(store_config_file)
        default_dept, _, _ = get_item_dept_dicts_and_print_order_from_store_config_file(default_store_file)

        placed = set()
        for dept in store_order:
            for item in self.grocery_list:
                item_name = item.split(':')[0]
                if item_name in store_dept and store_dept[item_name] == dept:
                    self.grocery_list_by_store_order.append(f'{dept} -- {item}')
                    placed.add(item_name)
                elif item_name in default_dept and default_dept[item_name] == dept:
                    self.grocery_list_by_store_order.append(f'{dept} -- {item}')
                    placed.add(item_name)

        for item in self.grocery_list:
            if item.split(':')[0] not in placed:
                self.grocery_list_by_store_order.append(f'No Department Listed -- {item}')

    def write_store_ordered_grocery_list_to_file(self, file_name):
        if not self.grocery_list_by_store_order:
            print('grocery_list_by_store_order is empty.')
            return
        with open(Path(file_name), 'w') as f:
            f.write('*** Recipes this Week ***\n')
            for r in self.recipe_list:
                f.write(r.name + '\n')
            f.write('*************************\n\n')
            for line in self.grocery_list_by_store_order:
                f.write(line + '\n')

    # -- SQLite usage tracking (replaces .tmstmp flat file) ----------------

    def read_time_stamp_file(
        self,
        db_path,
        date_for_timedelta: datetime.date = datetime.date.today(),
        days_for_timedelta: int = 21,
    ) -> None:
        """Tag recipes as recently-used / not-recently-used using TimestampDB."""
        from timestamp_db import TimestampDB
        cutoff = date_for_timedelta - datetime.timedelta(days=days_for_timedelta)
        with TimestampDB(db_path) as db:
            recently_used = db.get_recipes_used_since(cutoff)
        for recipe in self.recipe_list:
            if recipe.name in recently_used:
                recipe.add_tag("recently-used")
            else:
                recipe.add_tag("not-recently-used")

    def write_recipe_usage_data(
        self,
        db_path,
        mark_recipes_with_this_date: datetime.date = datetime.date.today(),
        read_or_append: str = "a",  # kept for API compatibility; DB always upserts
    ) -> None:
        """Record selected recipes in the SQLite DB via TimestampDB."""
        from timestamp_db import TimestampDB
        with TimestampDB(db_path) as db:
            for recipe in self.recipe_list:
                if not recipe.is_grocery_staples_recipe:
                    db.record_usage(recipe.name, mark_recipes_with_this_date)

    # -- Recipe distance / stats -------------------------------------------

    def generate_ingredient_count(self):
        self.ingredient_count_dict = {}
        for r in self.recipe_list:
            for ing in r.ingredient_list:
                self.ingredient_count_dict[ing.name] = self.ingredient_count_dict.get(ing.name, 0) + 1
        for name, count in self.ingredient_count_dict.items():
            print(f'{name}: {count}')

    def calculate_recipe_distances(self):
        for recipe in self.recipe_list:
            for other in self.recipe_list:
                if recipe.name != other.name \
                        and not recipe.is_grocery_staples_recipe \
                        and not other.is_grocery_staples_recipe:
                    recipe.calculate_distance_from_another_recipe(other)

    def print_recipe_distances(self):
        self.calculate_recipe_distances()
        for recipe in self.recipe_list:
            print('---------------------------------------')
            print(f'Distances from {recipe.name}')
            for name, dist in recipe.distance_to_recipe_dict.items():
                print(f'{name}: {dist}')

    def write_recipe_stats_to_files(self, directory='../recipes/'):
        out_dir = Path(directory) / 'data'
        out_dir.mkdir(parents=True, exist_ok=True)
        self.calculate_recipe_distances()

        with open(out_dir / 'dist_by_recipe.data', 'w') as f:
            for recipe in self.recipe_list:
                sorted_dists = sorted(recipe.distance_to_recipe_dict.items(), key=lambda x: x[1], reverse=True)
                f.write(f'\n\n---------------------------------------\n')
                f.write(f'Distances from {recipe.name}\n---------------------------------------\n')
                for name, dist in sorted_dists:
                    f.write(f'{name}: {dist}\n')

        with open(out_dir / 'dist_by_dist.data', 'w') as f:
            pairs: dict = {}
            for recipe in self.recipe_list:
                for other in self.recipe_list:
                    if recipe.name != other.name \
                            and not recipe.is_grocery_staples_recipe \
                            and not other.is_grocery_staples_recipe:
                        key = ' ----> '.join(sorted([recipe.name, other.name]))
                        pairs[key] = recipe.distance_to_recipe_dict.get(other.name, 0)
            for key, dist in sorted(pairs.items(), key=lambda x: x[1], reverse=True):
                f.write(f'{key}: {dist}\n')
