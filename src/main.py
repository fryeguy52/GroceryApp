__author__ = 'Joe'

import datetime

import grocery_gui
import grocery_functions

if __name__ == "__main__":
    grocery_functions.check_recipe_format()
    all_recipes_name_list = grocery_functions.get_recipe_names("..\\recipes")
    selected_recepies = []
    grocery_list=[]
    grocery_gui.recipeGUI(all_recipes_name_list, selected_recepies)
    for recipe in selected_recepies:
            grocery_list += grocery_functions.get_ingredients_from_recipe_file("..\\recipes\\"+recipe+".txt")
    grocery_list=grocery_functions.condense_grocery_list(grocery_list)
    grocery_functions.sort_and_print_grocery_List(grocery_list, "Smiths-Eu-JT-ItemDepartments.txt")

