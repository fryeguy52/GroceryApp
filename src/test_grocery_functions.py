"""
test_grocery_functions.py
Unit tests for GroceryApp — updated for refactored module structure.
"""
__author__ = 'Joe'

import sys
import datetime
import unittest
from pathlib import Path

# Allow imports from src/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Ingredient, Recipe, RecipeCollection
from timestamp_db import TimestampDB

_TEST_RECIPES = Path(__file__).parent / "test-recipes"
_BROKEN       = Path(__file__).parent / "broken-test-recipes"
_TMP_DB       = Path(__file__).parent / "_test_timestamps.db"


class TestIngredient(unittest.TestCase):

    def test_valid_input(self):
        ing = Ingredient("1, cup, onion")
        self.assertEqual(ing.get_name(),   "onion")
        self.assertEqual(ing.get_unit(),   "cup")
        self.assertEqual(ing.get_number(), "1")

    def test_plural_stripping(self):
        ing = Ingredient("1, cups, onions")
        self.assertEqual(ing.get_name(), "onion")
        self.assertEqual(ing.get_unit(), "cup")

    def test_case_insensitive(self):
        ing = Ingredient("1, CuPs, OnIoNs")
        self.assertEqual(ing.get_name(), "onion")
        self.assertEqual(ing.get_unit(), "cup")

    def test_potato_normalisation(self):
        ing = Ingredient("1, cup, potatoes")
        self.assertEqual(ing.get_name(), "potato")

    def test_unit_normalisation(self):
        self.assertEqual(Ingredient("2, tablespoons, butter").get_unit(), "tablespoon")
        self.assertEqual(Ingredient("1, lbs, beef").get_unit(), "lb")
        self.assertEqual(Ingredient("3, teaspoons, salt").get_unit(), "teaspoon")

    def test_invalid_input_too_many_commas(self):
        ing = Ingredient("input that, is, totally, wrong, , ,")
        self.assertIn("invalid input line", ing.get_name())

    def test_invalid_input_too_few_commas(self):
        ing = Ingredient("1 Cup, Onion")
        self.assertIn("invalid input line", ing.get_name())


class TestRecipe(unittest.TestCase):

    def _load(self, filename):
        return Recipe(_TEST_RECIPES / filename)

    def test_name_from_filename(self):
        r = self._load("Healthy Roasted Chicken and Veggies (one pan).txt")
        self.assertEqual(r.get_name(), "Healthy Roasted Chicken and Veggies (one pan)")

    def test_ingredients_sorted(self):
        r = self._load("Healthy Roasted Chicken and Veggies (one pan).txt")
        names = [i.name for i in r.get_ingredient_list()]
        self.assertEqual(names, sorted(names))

    def test_instructional_text_present(self):
        r = self._load("Healthy Roasted Chicken and Veggies (one pan).txt")
        self.assertTrue(len(r.get_instructional_text()) > 0)


class TestRecipeCollection(unittest.TestCase):

    def _collection_from_dir(self, d=_TEST_RECIPES):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(d)
        return rc

    def test_add_recipe_individually(self):
        rc = RecipeCollection()
        for name in [
            "Healthy Roasted Chicken and Veggies (one pan).txt",
            "Cajun Chicken & Rice.txt",
            "Chicken Curry in a Hurry.txt",
        ]:
            rc.add_recipe(Recipe(_TEST_RECIPES / name))
        self.assertIn("Cajun Chicken & Rice", rc.get_recipe_names())

    def test_grocery_list_potato_summing(self):
        rc = self._collection_from_dir()
        gl = rc.get_grocery_list()
        potato_line = next((l for l in gl if l.startswith("potato:")), None)
        self.assertIsNotNone(potato_line)

    def test_grocery_list_no_garbled_units(self):
        rc = self._collection_from_dir()
        for line in rc.get_grocery_list():
            _, _, amounts = line.partition(":")
            for part in amounts.split(","):
                self.assertFalse(part.rstrip().endswith(" "),
                                 msg=f"Garbled unit in: {line!r}")

    def test_filter_by_tag(self):
        rc = self._collection_from_dir()
        filtered = rc.get_recipe_names(["asian"])
        self.assertIn("Chicken Curry in a Hurry", filtered)

    def test_filter_no_match(self):
        rc = self._collection_from_dir()
        result = rc.get_recipe_names(["pork"])
        self.assertIn("No recipes match", result[0])

    def test_format_error_detection(self):
        rc = self._collection_from_dir(_BROKEN)
        errors = rc.get_recipe_file_format_errors()
        self.assertTrue(any("invalid input line" in e for e in errors))
        self.assertTrue(any("not a valid heading" in e for e in errors))
        self.assertTrue(any("Missing one of the following tags" in e for e in errors))

    def test_recipe_distance_bug_fixed(self):
        rc = self._collection_from_dir()
        names = rc.get_recipe_names()
        if len(names) < 2:
            self.skipTest("Need at least 2 recipes")
        r1 = rc.get_recipe_by_name(names[0])
        r2 = rc.get_recipe_by_name(names[1])
        r1.calculate_distance_from_another_recipe(r2)
        dist = r1.distance_to_recipe_dict.get(r2.name)
        self.assertIsNotNone(dist)
        self.assertGreaterEqual(dist, 0.0)
        self.assertLessEqual(dist, 1.0)


class TestTimestampDB(unittest.TestCase):

    def setUp(self):
        if _TMP_DB.exists():
            _TMP_DB.unlink()
        self.db = TimestampDB(_TMP_DB)

    def tearDown(self):
        if _TMP_DB.exists():
            _TMP_DB.unlink()

    def test_record_and_retrieve(self):
        self.db.record_usage("Chili", datetime.date(2024, 3, 1))
        recent = self.db.get_recipes_used_since(datetime.date(2024, 2, 1))
        self.assertIn("Chili", recent)

    def test_cutoff_excludes_old(self):
        self.db.record_usage("Old Recipe", datetime.date(2020, 1, 1))
        recent = self.db.get_recipes_used_since(datetime.date(2024, 1, 1))
        self.assertNotIn("Old Recipe", recent)

    def test_duplicate_insert_is_idempotent(self):
        d = datetime.date(2024, 5, 10)
        self.db.record_usage("Tacos", d)
        self.db.record_usage("Tacos", d)
        taco_rows = [r for r in self.db.get_all_usage() if r[0] == "Tacos"]
        self.assertEqual(len(taco_rows), 1)

    def test_get_last_used(self):
        self.db.record_usage("Soup", datetime.date(2024, 1, 10))
        self.db.record_usage("Soup", datetime.date(2024, 3, 20))
        self.assertEqual(self.db.get_last_used("Soup"), datetime.date(2024, 3, 20))

    def test_get_last_used_unknown_recipe(self):
        self.assertIsNone(self.db.get_last_used("Ghost Recipe"))

    def test_tmstmp_path_redirects_to_db(self):
        db2 = TimestampDB(_TMP_DB.with_suffix(".tmstmp"))
        self.assertEqual(db2.db_path.suffix, ".db")

    def test_recipe_collection_integration(self):
        rc = RecipeCollection()
        rc.add_all_recipes_in_dir(_TEST_RECIPES)
        self.db.record_usage("Cajun Chicken & Rice", datetime.date(2020, 10, 10))
        self.db.record_usage("Chicken Curry in a Hurry", datetime.date(2020, 10, 5))
        rc.read_time_stamp_file(_TMP_DB, datetime.date(2020, 10, 13), days_for_timedelta=21)
        self.assertIn("recently-used",
                      rc.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertIn("not-recently-used",
                      rc.get_recipe_by_name(
                          "Healthy Roasted Chicken and Veggies (one pan)").tags)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=2).run(suite)
