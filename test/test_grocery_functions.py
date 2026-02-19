__author__ = 'Joe'
import sys
import datetime
import unittest
from pathlib import Path

# Allow imports from src/
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# FIX: classes moved to models.py in the refactor.
# Import them from there, and also expose via grocery_functions
# so the original import style still works.
from models import Ingredient, Recipe, RecipeCollection
import grocery_functions
grocery_functions.Ingredient        = Ingredient
grocery_functions.Recipe            = Recipe
grocery_functions.RecipeCollection  = RecipeCollection

from timestamp_db import TimestampDB

_TEST_RECIPES   = Path(__file__).parent / 'test-recipes'
_BROKEN_RECIPES = Path(__file__).parent / 'broken-test-recipes'
_TMSTMP_FIXTURE = _TEST_RECIPES / 'good_recipe_time_stamps.tmstmp'
_TMP_DB         = Path(__file__).parent / '_test_timestamps.db'


def _make_db_from_tmstmp(tmstmp_path: Path, db_path: Path) -> TimestampDB:
    """
    Convert a legacy .tmstmp fixture into a temporary SQLite DB for testing.
    Handles the non-ISO date '2020-9-24' (single-digit month/day) used in
    the fixture file.
    """
    if db_path.exists():
        db_path.unlink()
    db = TimestampDB(db_path)
    with tmstmp_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name_part, _, date_part = line.partition(':')
            date_part = date_part.strip()
            # Normalise single-digit month/day to ISO format
            parts = date_part.split('-')
            if len(parts) == 3:
                y, m, d = parts
                date = datetime.date(int(y), int(m), int(d))
                db.record_usage(name_part.strip(), date)
    return db


class TestIngredient(unittest.TestCase):

    def test_Ingedient_class_valid_input(self):
        ing1 = Ingredient("1, cup, onion")
        self.assertEqual(ing1.get_name(),   "onion")
        self.assertEqual(ing1.get_unit(),   "cup")
        self.assertEqual(ing1.get_number(), "1")

        ing1 = Ingredient("1, cups, onions")
        self.assertEqual(ing1.get_name(), "onion")
        self.assertEqual(ing1.get_unit(), "cup")

        ing1 = Ingredient("1, CuPs, OnIoNs")
        self.assertEqual(ing1.get_name(), "onion")
        self.assertEqual(ing1.get_unit(), "cup")

        ing1 = Ingredient("1, Cup, Onion")
        self.assertEqual(ing1.get_name(), "onion")
        self.assertEqual(ing1.get_unit(), "cup")

        ing1 = Ingredient("1, cup, potatoes")
        self.assertEqual(ing1.get_name(), "potato")

    def test_Ingedient_class_invalid_input(self):
        ing1 = Ingredient("input that, is, totally, wrong, , ,")
        self.assertIn("invalid input line", ing1.get_name())
        self.assertIn("invalid input line", ing1.get_unit())
        self.assertIn("invalid input line", ing1.get_number())

        ing1 = Ingredient("1 Cup, Onion")
        self.assertIn("invalid input line", ing1.get_name())
        self.assertIn("invalid input line", ing1.get_unit())
        self.assertIn("invalid input line", ing1.get_number())


class TestRecipe(unittest.TestCase):

    def test_Recipe_class(self):
        recipe1 = Recipe(_TEST_RECIPES / "Healthy Roasted Chicken and Veggies (one pan).txt")
        self.assertEqual(recipe1.get_name(), "Healthy Roasted Chicken and Veggies (one pan)")

        # Instructional text should contain the recipe section content
        text = recipe1.get_instructional_text()
        self.assertIn("Preheat oven to 500 degree F.", text)
        self.assertIn("Chop all the veggies", text)
        self.assertIn("Bake for 15 minutes", text)

        # Ingredients are sorted alphabetically
        names = [i.name for i in recipe1.get_ingredient_list()]
        self.assertEqual(names, sorted(names))
        self.assertIn("bell pepper", names)
        self.assertIn("chicken breast", names)
        self.assertIn("olive oil", names)
        self.assertIn("tomato", names)
        self.assertIn("zucchini", names)


class TestRecipeCollection(unittest.TestCase):

    def _load_test_recipes(self) -> RecipeCollection:
        rc = RecipeCollection()
        for name in [
            "Healthy Roasted Chicken and Veggies (one pan).txt",
            "Cajun Chicken & Rice.txt",
            "Chicken Curry in a Hurry.txt",
            "Chicken_Zucchini_and_Prosciutto.txt",
            "Kielbasa, Pepper, Onion and Potato Hash.txt",
        ]:
            rc.add_recipe(Recipe(_TEST_RECIPES / name))
        return rc

    def test_RecipeCollection_class_individual_add(self):
        rc = self._load_test_recipes()
        gl = rc.get_grocery_list()

        # Potatoes should be summed to 3 large
        self.assertTrue(any("potato" in item and "3" in item for item in gl),
                        msg=f"Expected 3 potatoes in grocery list, got: {gl}")

        # All recipe names should be present
        names = rc.get_recipe_names()
        self.assertIn("Healthy Roasted Chicken and Veggies (one pan)", names)
        self.assertIn("Cajun Chicken & Rice", names)
        self.assertIn("Chicken Curry in a Hurry", names)
        self.assertIn("Chicken_Zucchini_and_Prosciutto", names)
        self.assertIn("Kielbasa, Pepper, Onion and Potato Hash", names)

    def test_RecipeCollection_class_directory_add(self):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(_TEST_RECIPES)
        gl = rc.get_grocery_list()

        self.assertTrue(any("potato" in item and "3" in item for item in gl),
                        msg=f"Expected 3 potatoes in grocery list, got: {gl}")

        names = rc.get_recipe_names()
        self.assertIn("Healthy Roasted Chicken and Veggies (one pan)", names)
        self.assertIn("Cajun Chicken & Rice", names)
        self.assertIn("Chicken Curry in a Hurry", names)
        self.assertIn("Chicken_Zucchini_and_Prosciutto", names)
        self.assertIn("Kielbasa, Pepper, Onion and Potato Hash", names)

    def test_RecipeCollection_class_filter_by_tag(self):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(_TEST_RECIPES)

        # No filter — all 5 recipes
        self.assertEqual(len(rc.get_recipe_names([])), 5)

        # Filter by 'asian' — only Chicken Curry in a Hurry
        filtered = rc.get_recipe_names(['asian'])
        self.assertIn("Chicken Curry in a Hurry", filtered)
        self.assertEqual(len(filtered), 1)

        # Filter by tag with no matches
        result = rc.get_recipe_names(['pork'])
        self.assertTrue(result[0].startswith("No recipes match"))

        # Filter by two tags
        filtered = rc.get_recipe_names(['easy', 'chicken'])
        self.assertIn("Cajun Chicken & Rice", filtered)
        self.assertIn("Chicken Curry in a Hurry", filtered)
        self.assertEqual(len(filtered), 2)

    def test_file_format_error_detection(self):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(_BROKEN_RECIPES)
        errors = rc.get_recipe_file_format_errors()

        # Invalid ingredient lines
        self.assertTrue(any("invalid input line" in e and "1 lb, chicken breasts" in e
                            for e in errors), msg=f"Errors: {errors}")
        self.assertTrue(any("invalid input line" in e and "4, cup bell peppers" in e
                            for e in errors), msg=f"Errors: {errors}")

        # Invalid headings
        self.assertTrue(any("wrong_header is not a valid heading" in e for e in errors))
        self.assertTrue(any("misspelled is not a valid heading" in e for e in errors))

        # Missing required tags
        self.assertTrue(any("poo_sandwich" in e and "summer" in e for e in errors))
        self.assertTrue(any("poo_sandwich" in e and "breakfast" in e for e in errors))
        self.assertTrue(any("poo_sandwich" in e and "stove" in e for e in errors))

    def test_RecipeCollection_class_time_stamps_read(self):
        # Build a SQLite DB from the legacy fixture file
        db = _make_db_from_tmstmp(_TMSTMP_FIXTURE, _TMP_DB)

        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(_TEST_RECIPES)
        rc.read_time_stamp_file(_TMP_DB, datetime.date(2020, 10, 13), days_for_timedelta=21)

        # Within 21 days of 2020-10-13: Cajun (10-08), Curry (10-01), Zucchini (9-24)
        self.assertIn("recently-used",
                      rc.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertIn("recently-used",
                      rc.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertIn("recently-used",
                      rc.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertNotIn("recently-used",
                         rc.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertNotIn("recently-used",
                         rc.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

        self.assertNotIn("not-recently-used",
                         rc.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertIn("not-recently-used",
                      rc.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertIn("not-recently-used",
                      rc.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

        # Same fixture, 10-day window — only Cajun (10-08) is recent
        db2_path = _TMP_DB.with_name("_test_timestamps_10d.db")
        _make_db_from_tmstmp(_TMSTMP_FIXTURE, db2_path)
        rc2 = RecipeCollection()
        rc2.add_all_recipes_in_dir(_TEST_RECIPES)
        rc2.read_time_stamp_file(db2_path, datetime.date(2020, 10, 13), days_for_timedelta=10)

        self.assertIn("recently-used",
                      rc2.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertNotIn("recently-used",
                         rc2.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertNotIn("recently-used",
                         rc2.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertIn("not-recently-used",
                      rc2.get_recipe_by_name("Chicken Curry in a Hurry").tags)

        # Cleanup
        for p in [_TMP_DB, db2_path]:
            if p.exists():
                p.unlink()

    def test_RecipeCollection_class_time_stamps_write(self):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(_TEST_RECIPES)

        # Before reading timestamps, no tags set
        for name in rc.get_recipe_names():
            self.assertNotIn("recently-used",     rc.get_recipe_by_name(name).tags)
            self.assertNotIn("not-recently-used",  rc.get_recipe_by_name(name).tags)

        # Write today's date for all recipes, then read back
        write_db = _TMP_DB.with_name("_test_write_timestamps.db")
        if write_db.exists():
            write_db.unlink()

        rc.write_recipe_usage_data(write_db, mark_recipes_with_this_date=datetime.date(2020, 10, 13))

        rc2 = RecipeCollection()
        rc2.add_all_recipes_in_dir(_TEST_RECIPES)
        rc2.read_time_stamp_file(write_db, datetime.date(2020, 10, 13), days_for_timedelta=21)

        for name in rc2.get_recipe_names():
            self.assertIn("recently-used",     rc2.get_recipe_by_name(name).tags)
            self.assertNotIn("not-recently-used", rc2.get_recipe_by_name(name).tags)

        if write_db.exists():
            write_db.unlink()

    def test_Recipe_class_difference(self):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(Path(__file__).parent.parent / 'recipes')
        rc.generate_ingredient_count()
        rc.write_recipe_stats_to_files()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=2).run(suite)
