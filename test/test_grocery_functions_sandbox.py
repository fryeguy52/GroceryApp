__author__ = 'Joe'
import sys
sys.path.insert(0,'../src/')

import grocery_functions
import unittest

class TestGroceryFuncs(unittest.TestCase):

    def test_RecipeCollection_class_filter_by_tag(self):
        recipe_collection_3 = grocery_functions.RecipeCollection()
        recipe_collection_3.get_all_recipes_in_dir("test-recipes\\")

        recipe_collection_3.make_ingredient_list()
        self.assertTrue("potato: 3 large" in recipe_collection_3.get_grocery_list())

        self.assertTrue("olive oil: 1 , 7.5 tablespoon" in recipe_collection_3.get_grocery_list() or
                        "olive oil: 7.5 tablespoon, 1 " in recipe_collection_3.get_grocery_list())


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)
    unittest.TextTestRunner(verbosity=2).run(suite)