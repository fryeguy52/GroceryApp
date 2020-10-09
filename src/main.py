__author__ = 'Joe'

import datetime

import grocery_gui
import grocery_functions
import trello_functions

if __name__ == "__main__":
    grocery_file_errors=grocery_functions.check_recipe_format()
    grocery_functions.update_default_ing_dept_file(grocery_functions.get_all_ingredients("..\\recipes"))

    all_of_the_recipes = grocery_functions.RecipeCollection()
    all_of_the_recipes.get_all_recipes_in_dir("..\\recipes")

    if grocery_file_errors == []:
        selected_recepes = []
        grocery_list=[]
        grocery_gui.recipeGUI(selected_recepes)
        recipes_for_the_week=grocery_functions.RecipeCollection()
        for recipe_name in selected_recepes:
                #trello_functions.post_recipe_to_trello(recipe)
                grocery_list += grocery_functions.get_ingredients_from_recipe_file("..\\recipes\\"+recipe_name+".txt")
                recipes_for_the_week.add_recipe(all_of_the_recipes.get_recipe_by_name(recipe_name))
        grocery_list=grocery_functions.condense_grocery_list(grocery_list)
        grocery_list_new=recipes_for_the_week.get_grocery_list_by_store_order("JT_Alb.txt")
        recipes_for_the_week.write_store_ordered_grocery_list_to_file("test_output.txt")

        print(grocery_list)
        print(grocery_list_new)

        grocery_functions.sort_and_print_grocery_list_file(selected_recepes, grocery_list, "JT_Alb.txt")
    else:
        print(grocery_file_errors)

