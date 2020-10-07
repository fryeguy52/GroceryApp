__author__ = 'Joe'

import datetime

import grocery_gui
import grocery_functions
import trello_functions

if __name__ == "__main__":
    grocery_file_errors=grocery_functions.check_recipe_format()
    grocery_functions.update_default_ing_dept_file(grocery_functions.get_all_ingredients("..\\recipes"))

    if grocery_file_errors == []:
        selected_recepes = []
        grocery_list=[]
        grocery_gui.recipeGUI(selected_recepes)
        for recipe in selected_recepes:
                #trello_functions.post_recipe_to_trello(recipe)
                grocery_list += grocery_functions.get_ingredients_from_recipe_file("..\\recipes\\"+recipe+".txt")
        grocery_list=grocery_functions.condense_grocery_list(grocery_list)
        grocery_functions.sort_and_print_grocery_list_file(selected_recepes, grocery_list, "JT_Alb.txt")
    else:
        print(grocery_file_errors)

