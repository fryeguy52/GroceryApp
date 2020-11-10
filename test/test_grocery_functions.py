__author__ = 'Joe'
import sys
sys.path.insert(0,'../src/')

import grocery_functions
import unittest
import datetime

class TestGroceryFuncs(unittest.TestCase):

    def test_Ingedient_class_valid_input(self):
        ing1=grocery_functions.Ingredient("1, cup, onion")
        self.assertTrue(ing1.get_name()=="onion")
        self.assertTrue(ing1.get_unit() == "cup")
        self.assertTrue(ing1.get_number() == "1")
        ing1 = grocery_functions.Ingredient("1, cups, onions")
        self.assertTrue(ing1.get_name() == "onion")
        self.assertTrue(ing1.get_unit() == "cup")
        ing1 = grocery_functions.Ingredient("1, CuPs, OnIoNs")
        self.assertTrue(ing1.get_name() == "onion")
        self.assertTrue(ing1.get_unit() == "cup")
        ing1 = grocery_functions.Ingredient("1, Cup, Onion")
        self.assertTrue(ing1.get_name() == "onion")
        self.assertTrue(ing1.get_unit() == "cup")
        ing1 = grocery_functions.Ingredient("1, cup, potatoes")
        self.assertTrue(ing1.get_name() == "potato")

    def test_Ingedient_class_invalid_input(self):
        ing1 = grocery_functions.Ingredient("input that, is, totally, wrong, , ,")
        self.assertTrue(ing1.get_name() == "invalid input line: input that, is, totally, wrong, , ,")
        self.assertTrue(ing1.get_unit() == "invalid input line: input that, is, totally, wrong, , ,")
        self.assertTrue(ing1.get_number() == "invalid input line: input that, is, totally, wrong, , ,")
        ing1 = grocery_functions.Ingredient("1 Cup, Onion")
        self.assertTrue(ing1.get_name() == "invalid input line: 1 Cup, Onion")
        self.assertTrue(ing1.get_unit() == "invalid input line: 1 Cup, Onion")
        self.assertTrue(ing1.get_number() == "invalid input line: 1 Cup, Onion")

    def test_Recipe_class(self):
        recipe1 = grocery_functions.Recipe("test-recipes\Healthy Roasted Chicken and Veggies (one pan).txt")
        self.assertTrue(recipe1.get_name() == "Healthy Roasted Chicken and Veggies (one pan)")
        self.assertTrue("Ingredients" in recipe1.get_instructional_text())
        self.assertTrue("2, medium chicken breasts, chopped" in recipe1.get_instructional_text())
        self.assertTrue("1, cup, bell pepper chopped (any colors you like)" in recipe1.get_instructional_text())
        self.assertTrue("1, ,onion chopped" in recipe1.get_instructional_text())
        self.assertTrue("1, , zucchini chopped  Coupons" in recipe1.get_instructional_text())
        self.assertTrue("1, cup, broccoli florets" in recipe1.get_instructional_text())
        self.assertTrue("1, cup tomatoes, chopped or plum/grape" in recipe1.get_instructional_text())
        self.assertTrue("2, tablespoons olive oil" in recipe1.get_instructional_text())
        self.assertTrue("1, teaspoon salt" in recipe1.get_instructional_text())
        self.assertTrue("1, teaspoon black pepper" in recipe1.get_instructional_text())
        self.assertTrue("1 teaspoon italian seasoning" in recipe1.get_instructional_text())
        self.assertTrue("1, teaspoon paprika (optional)" in recipe1.get_instructional_text())
        self.assertTrue("Instructions" in recipe1.get_instructional_text())
        self.assertTrue("Preheat oven to 500 degree F. " in recipe1.get_instructional_text())
        self.assertTrue("Chop all the veggies into large pieces. In another cutting board chop the chicken into cubes. "
                        in recipe1.get_instructional_text())
        self.assertTrue("Place the chicken and veggies in a medium roasting dish or sheet pan. Add the olive oil, "
                        in recipe1.get_instructional_text())
        self.assertTrue("salt and pepper, italian seasoning, and paprika. Toss to combine." in
                        recipe1.get_instructional_text())
        self.assertTrue("Bake for 15 minutes or until the veggies are charred and chicken is cooked. Enjoy with rice,"
                        " pasta, or a salad." in recipe1.get_instructional_text())
        self.assertTrue(recipe1.get_ingredient_list()[0].name == "bell pepper")
        self.assertTrue(recipe1.get_ingredient_list()[3].name == "chicken breast")
        self.assertTrue(recipe1.get_ingredient_list()[5].name == "olive oil")
        self.assertTrue(recipe1.get_ingredient_list()[-2].name == "tomato")
        self.assertTrue(recipe1.get_ingredient_list()[-1].name == "zucchini")

    def test_RecipeCollection_class_individual_add(self):
        recipe1 = grocery_functions.Recipe("test-recipes\Healthy Roasted Chicken and Veggies (one pan).txt")
        recipe2 = grocery_functions.Recipe("test-recipes\Cajun Chicken & Rice.txt")
        recipe3 = grocery_functions.Recipe("test-recipes\Chicken Curry in a Hurry.txt")
        recipe4 = grocery_functions.Recipe("test-recipes\Chicken_Zucchini_and_Prosciutto.txt")
        recipe5 = grocery_functions.Recipe("test-recipes\Kielbasa, Pepper, Onion and Potato Hash.txt")

        recipe_collection_1=grocery_functions.RecipeCollection()
        recipe_collection_1.add_recipe(recipe1)
        recipe_collection_1.add_recipe(recipe2)
        recipe_collection_1.add_recipe(recipe3)
        recipe_collection_1.add_recipe(recipe4)
        recipe_collection_1.add_recipe(recipe5)

        recipe_collection_1.make_ingredient_list()
        self.assertTrue("potato: 3 large" in recipe_collection_1.get_grocery_list())

        self.assertTrue("olive oil: 1 , 7.5 tablespoon" in recipe_collection_1.get_grocery_list() or
                        "olive oil: 7.5 tablespoon, 1 " in recipe_collection_1.get_grocery_list())

        self.assertTrue("chicken breast: 6.0 , 1 lb" in recipe_collection_1.get_grocery_list() or
                        "chicken breast: 1 lb, 6.0 " in recipe_collection_1.get_grocery_list())

        self.assertTrue("Healthy Roasted Chicken and Veggies (one pan)" in recipe_collection_1.get_recipe_names())
        self.assertTrue("Cajun Chicken & Rice" in recipe_collection_1.get_recipe_names())
        self.assertTrue("Chicken Curry in a Hurry" in recipe_collection_1.get_recipe_names())
        self.assertTrue("Chicken_Zucchini_and_Prosciutto" in recipe_collection_1.get_recipe_names())
        self.assertTrue("Kielbasa, Pepper, Onion and Potato Hash" in recipe_collection_1.get_recipe_names())

    def test_RecipeCollection_class_directory_add(self):
        recipe_collection_2 = grocery_functions.RecipeCollection()
        recipe_collection_2.add_all_recipes_in_dir("test-recipes\\")

        recipe_collection_2.make_ingredient_list()
        self.assertTrue("potato: 3 large" in recipe_collection_2.get_grocery_list())
        self.assertTrue("olive oil: 1 , 7.5 tablespoon" in recipe_collection_2.get_grocery_list() or
                        "olive oil: 7.5 tablespoon, 1 " in recipe_collection_2.get_grocery_list())

        self.assertTrue("chicken breast: 6.0 , 1 lb" in recipe_collection_2.get_grocery_list() or
                        "chicken breast: 1 lb, 6.0 " in recipe_collection_2.get_grocery_list())

        self.assertTrue("Healthy Roasted Chicken and Veggies (one pan)" in recipe_collection_2.get_recipe_names())
        self.assertTrue("Cajun Chicken & Rice" in recipe_collection_2.get_recipe_names())
        self.assertTrue("Chicken Curry in a Hurry" in recipe_collection_2.get_recipe_names())
        self.assertTrue("Chicken_Zucchini_and_Prosciutto" in recipe_collection_2.get_recipe_names())
        self.assertTrue("Kielbasa, Pepper, Onion and Potato Hash" in recipe_collection_2.get_recipe_names())

    def test_RecipeCollection_class_filter_by_tag(self):
        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.add_all_recipes_in_dir("test-recipes\\")

        filtered_list=recipe_collection_3.get_recipe_names([])
        self.assertTrue("Healthy Roasted Chicken and Veggies (one pan)" in filtered_list)
        self.assertTrue("Cajun Chicken & Rice" in filtered_list)
        self.assertTrue("Chicken Curry in a Hurry" in filtered_list)
        self.assertTrue("Chicken_Zucchini_and_Prosciutto" in filtered_list)
        self.assertTrue("Kielbasa, Pepper, Onion and Potato Hash" in filtered_list)
        self.assertTrue(len(filtered_list) == 5)

        filtered_list = recipe_collection_3.get_recipe_names(['asian'])
        self.assertTrue("Chicken Curry in a Hurry" in filtered_list)
        self.assertTrue(len(filtered_list) == 1)

        filtered_list = recipe_collection_3.get_recipe_names(['pork'])
        self.assertTrue("No recipes match the tags: ['pork']" in filtered_list)
        self.assertTrue(len(filtered_list) == 1)

        filtered_list = recipe_collection_3.get_recipe_names(['easy', 'chicken'])
        self.assertTrue("Cajun Chicken & Rice" in filtered_list)
        self.assertTrue("Chicken Curry in a Hurry" in filtered_list)
        self.assertTrue(len(filtered_list) == 2)

    def test_file_format_error_detection(self):
        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.add_all_recipes_in_dir("broken-test-recipes\\")

        all_recipe_file_format_errors = recipe_collection_3.get_recipe_file_format_errors()
        self.assertTrue('broken_recipe: invalid input line: 1 lb, chicken breasts\n' in all_recipe_file_format_errors)
        self.assertTrue('broken_recipe: invalid input line: 4, cup bell peppers\n' in all_recipe_file_format_errors)
        self.assertTrue('broken_recipe: wrong_header is not a valid heading' in all_recipe_file_format_errors)
        self.assertTrue('broken_recipe: misspelled is not a valid heading' in all_recipe_file_format_errors)
        self.assertTrue("poo_sandwich: Missing one of the following tags: ['summer', 'fall', 'winter', 'spring']" in all_recipe_file_format_errors)
        self.assertTrue("poo_sandwich: Missing one of the following tags: ['breakfast', 'lunch', 'dinner', 'side']" in all_recipe_file_format_errors)
        self.assertTrue("poo_sandwich: Missing one of the following tags: ['stove', 'grill', 'oven', 'crock pot', 'instant pot', 'no cooking']" in all_recipe_file_format_errors)

    def test_RecipeCollection_class_time_stamps_read(self):
        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.add_all_recipes_in_dir("test-recipes\\")

        recipe_collection_3.read_time_stamp_file("test-recipes\\good_recipe_time_stamps.tmstmp", datetime.date(2020,10,13))

        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

        self.assertTrue(not "not-recently-used"
                            in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)

        self.assertTrue(not "not-recently-used"
                            in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)

        self.assertTrue(not "not-recently-used"
                            in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)

        self.assertTrue("not-recently-used"
                        in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)

        self.assertTrue("not-recently-used"
                        in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.add_all_recipes_in_dir("test-recipes\\")

        recipe_collection_3.read_time_stamp_file("test-recipes\\good_recipe_time_stamps.tmstmp",
                                                 datetime.date(2020, 10, 13), 10)

        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertTrue(
            not "recently-used" in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name(
            "Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name(
            "Kielbasa, Pepper, Onion and Potato Hash").tags)

        self.assertTrue(not "not-recently-used"
                            in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)

        self.assertTrue("not-recently-used"
                            in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)

        self.assertTrue("not-recently-used"
                            in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)

        self.assertTrue("not-recently-used"
                        in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)

        self.assertTrue("not-recently-used"
                        in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

    def test_RecipeCollection_class_time_stamps_write(self):
        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.add_all_recipes_in_dir("test-recipes\\")

        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertTrue(not "recently-used" in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

        recipe_collection_3.write_recipe_usage_data("write_out_timestamps.tmstmp", read_or_append='w')
        recipe_collection_3.read_time_stamp_file("write_out_timestamps.tmstmp", datetime.date(2020, 10, 13))

        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertTrue("recently-used" in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Cajun Chicken & Rice").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Chicken Curry in a Hurry").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Chicken_Zucchini_and_Prosciutto").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Healthy Roasted Chicken and Veggies (one pan)").tags)
        self.assertTrue(not "not-recently-used" in recipe_collection_3.get_recipe_by_name("Kielbasa, Pepper, Onion and Potato Hash").tags)

    def test_Recipe_class_difference(self):
        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.add_all_recipes_in_dir("..\\recipes\\")

        recipe_collection_3.generate_ingredient_count()
        recipe_collection_3.write_recipe_stats_to_files()

    def suite(self):
        return unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)
    unittest.TextTestRunner(verbosity=2).run(suite)