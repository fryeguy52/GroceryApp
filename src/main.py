__author__ = 'Joe'

import datetime

import grocery_gui
import grocery_functions

if __name__ == "__main__":
    grocery_file_errors=grocery_functions.check_recipe_format()
    grocery_functions.make_all_ingredients_file()
    grocery_functions.update_default_ing_dept_file(grocery_functions.get_all_ingredients("..\\recipes"))
    if grocery_file_errors == []:
        all_recipes_name_list = grocery_functions.get_recipe_names("..\\recipes")
        selected_recepies = []
        grocery_list=[]
        grocery_gui.recipeGUI(all_recipes_name_list, selected_recepies)
        for recipe in selected_recepies:
                grocery_list += grocery_functions.get_ingredients_from_recipe_file("..\\recipes\\"+recipe+".txt")
        grocery_list=grocery_functions.condense_grocery_list(grocery_list)
        grocery_functions.sort_and_print_grocery_list_file(selected_recepies, grocery_list, "Smiths-Eu-JT-ItemDepartments.txt")

