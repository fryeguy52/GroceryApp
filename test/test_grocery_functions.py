__author__ = 'Joe'
import sys
sys.path.insert(0,'../src/')

import grocery_functions
import unittest

class TestGroceryFuncs(unittest.TestCase):

    def test_getRecipeNames(self):
        recipe_names = grocery_functions.get_recipe_names("test-recipes")
        self.assertTrue(recipe_names[0] == "Cajun Chicken & Rice")
        self.assertTrue(recipe_names[1] == "Chicken Curry in a Hurry")
        self.assertTrue(recipe_names[2] == 'Chicken_Zucchini_and_Prosciutto')
        self.assertTrue(recipe_names[3] == 'Healthy Roasted Chicken and Veggies (one pan)')
        self.assertTrue(recipe_names[4] == 'Kielbasa, Pepper, Onion and Potato Hash')

    def test_getIngredientsFromFile(self):
        list=grocery_functions.get_ingredients_from_recipe_file("test-recipes\Kielbasa, Pepper, Onion and Potato Hash.txt")
        self.assertTrue(list[0].name == 'turkey kielbasa')
        self.assertTrue(list[0].unit == 'ounce')
        self.assertTrue(list[0].number == '14')
        self.assertTrue(list[2].name == 'non-green bell pepper')
        self.assertTrue(list[2].unit == '')
        self.assertTrue(list[2].number == '1')
        self.assertTrue(list[6].name == 'salt')
        self.assertTrue(list[6].unit == '')
        self.assertTrue(list[6].number == '1')

    def test_getTagsFromFile(self):
        list=grocery_functions.get_tags_from_recipe_file("test-recipes\Chicken Curry in a Hurry.txt")
        self.assertTrue(list[0] == 'chicken')
        self.assertTrue(list[1] == 'easy')
        self.assertTrue(list[2] == 'stove')

    def test_getRecipeFromFile(self):
        recipe=grocery_functions.get_recipe_from_recipe_file("test-recipes\Healthy Roasted Chicken and Veggies (one pan).txt")
        self.assertTrue("1, cup, bell pepper chopped (any colors you like)" in recipe)
        self.assertTrue("1 teaspoon italian seasoning" in recipe)
        self.assertTrue("Place the chicken and veggies in a medium roasting dish or sheet pan. Add the olive oil, " in recipe)

    def test_condenseList(self):
        recipe_names = grocery_functions.get_recipe_names("test-recipes")
        grocery_list=[]
        for recipe in recipe_names:
            grocery_list += grocery_functions.get_ingredients_from_recipe_file("test-recipes\\"+recipe+".txt")
        grocery_list=grocery_functions.condense_grocery_list(grocery_list)
        # grocery_functions.print_grocery_list(grocery_list)
        # grocery_functions.sort_and_print_grocery_List(grocery_list, "Smiths-Eu-JT-ItemDepartments.txt")

    def test_getItemDeptDicts(self):
        grocery_functions.get_item_dept_dicts("Smiths-Eu-JT-ItemDepartments.txt")

    def test_checkRecipeFormat(self):
        errors=grocery_functions.check_recipe_format("test-recipes", False)
        self.assertTrue(errors == [])
        errors=grocery_functions.check_recipe_format("broken-test-recipes", False)
        self.assertTrue('invalid format, "1 lb, chicken breasts" in: broken-test-recipes//broken_recipe.txt' in errors)
        self.assertTrue('invalid heading, "wrong_header" in file: broken-test-recipes//broken_recipe.txt' in errors)
        self.assertTrue('invalid heading, "misspelled" in file: broken-test-recipes//broken_recipe.txt' in errors)

    def test_update_default_ing_dept_file(self):
        grocery_functions.update_default_ing_dept_file(grocery_functions.get_all_ingredients("test-recipes"))

    def suite(self):
        return unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)
    unittest.TextTestRunner(verbosity=2).run(suite)