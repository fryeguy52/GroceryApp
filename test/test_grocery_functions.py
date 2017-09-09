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
        list=grocery_functions.get_recipe_from_recipe_file("test-recipes\Healthy Roasted Chicken and Veggies (one pan).txt")
        self.assertTrue(list[2]=="1 cup bell pepper, chopped (any colors you like)")
        self.assertTrue(list[10]=="1 teaspoon italian seasoning")
        self.assertTrue(list[15]=="Place the chicken and veggies in a medium roasting dish or sheet pan. Add the olive oil, ")

    def test_matches(self):
        test_string = 'onion'
        self.assertTrue(grocery_functions.matches(test_string, test_string))
        self.assertTrue(grocery_functions.matches(test_string, 'onion'))
        self.assertTrue(grocery_functions.matches(test_string, 'Onion'))
        self.assertTrue(grocery_functions.matches(test_string, 'ONIONS'))
        self.assertTrue(grocery_functions.matches('oz', 'oz.'))
        self.assertTrue(grocery_functions.matches('ozs', 'oZ.'))

        self.assertFalse(grocery_functions.matches(test_string, 'red onion'))
        self.assertFalse(grocery_functions.matches(test_string, 'sonion'))

    def suite(self):
        return unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)
    unittest.TextTestRunner(verbosity=2).run(suite)