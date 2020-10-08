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
        list=grocery_functions.get_ingredients_from_recipe_file("test-recipes\Kielbasa, Pepper, "
                                                                "Onion and Potato Hash.txt")
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
        recipe=grocery_functions.get_recipe_from_recipe_file("test-recipes\Healthy Roasted Chicken and Veggies "
                                                             "(one pan).txt")
        self.assertTrue("1, cup, bell pepper chopped (any colors you like)" in recipe)
        self.assertTrue("1 teaspoon italian seasoning" in recipe)
        self.assertTrue("Place the chicken and veggies in a medium roasting dish or sheet pan. Add the olive oil, "
                        in recipe)

    def test_condenseList(self):
        recipe_names = grocery_functions.get_recipe_names("test-recipes")
        grocery_list=[]
        for recipe in recipe_names:
            grocery_list += grocery_functions.get_ingredients_from_recipe_file("test-recipes\\"+recipe+".txt")

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

    def test_Ingedient_class(self):
        ing1=grocery_functions.Ingredient("1, cup, onion")
        self.assertTrue(ing1.getName()=="onion")
        self.assertTrue(ing1.getUnit() == "cup")
        self.assertTrue(ing1.getNumber() == "1")
        ing1 = grocery_functions.Ingredient("1, cups, onions")
        self.assertTrue(ing1.getName() == "onion")
        self.assertTrue(ing1.getUnit() == "cup")
        ing1 = grocery_functions.Ingredient("1, CuPs, OnIoNs")
        self.assertTrue(ing1.getName() == "onion")
        self.assertTrue(ing1.getUnit() == "cup")
        ing1 = grocery_functions.Ingredient("1, Cup, Onion")
        self.assertTrue(ing1.getName() == "onion")
        self.assertTrue(ing1.getUnit() == "cup")
        ing1 = grocery_functions.Ingredient("1, cup, potatoes")
        self.assertTrue(ing1.getName() == "potato")
        ing1 = grocery_functions.Ingredient("input that, is, totally, wrong, , ,")
        self.assertTrue(ing1.getName() == "invalid input line: input that, is, totally, wrong, , ,")
        self.assertTrue(ing1.getUnit() == "invalid input line: input that, is, totally, wrong, , ,")
        self.assertTrue(ing1.getNumber() == "invalid input line: input that, is, totally, wrong, , ,")
        ing1 = grocery_functions.Ingredient("1 Cup, Onion")
        self.assertTrue(ing1.getName() == "invalid input line: 1 Cup, Onion")
        self.assertTrue(ing1.getUnit() == "invalid input line: 1 Cup, Onion")
        self.assertTrue(ing1.getNumber() == "invalid input line: 1 Cup, Onion")

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
        recipe_collection_2.get_all_recipes_in_dir("test-recipes\\")

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
        recipe_collection_3.get_all_recipes_in_dir("test-recipes\\")

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



    def suite(self):
        return unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroceryFuncs)
    unittest.TextTestRunner(verbosity=2).run(suite)