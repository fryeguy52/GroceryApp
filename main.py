__author__ = 'Joe'

import datetime

import groceryFileIO
import ingedientTools
import grocery_list
import grocery_options as GO
import grocery_gui

def initialize():
    grocery_opts=GO.grocery_options()
    master_ing_dict = groceryFileIO.read_ingredient_file('master_ingredient_list.json')
    master_recipe_list = groceryFileIO.read_recipe_file('master_recipe_list.json')
    my_grocery_list = grocery_list.GroceryList(master_ing_dict)
    my_grocery_list.print_order=grocery_opts.print_order
    ingedientTools.extract_ingredients(master_recipe_list, master_ing_dict)
    ingedientTools.add_ingredient_locations(master_ing_dict)
    groceryFileIO.write_ingredient_file(master_ing_dict, 'master_ingredient_list.json')

    return master_recipe_list, my_grocery_list, grocery_opts


if __name__ == "__main__":
    master_recipe_list, my_grocery_list, grocery_opts = initialize()
    if grocery_opts.print_config_vars is "yes":
        grocery_opts.print_options()

    if grocery_opts.mode is "GUI":
        selected_recepies = []
        all_recipes_name_list = []
        for recipe in master_recipe_list:
            all_recipes_name_list.append(recipe)
        grocery_gui.recipeGUI(all_recipes_name_list, selected_recepies)
        for recipe in master_recipe_list:
            if recipe in selected_recepies:
                my_grocery_list.add_from_recipe(master_recipe_list.get(recipe))
        my_grocery_list.write_to_file('grocery_list_'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")+'.txt', grocery_opts.output_filetype)

    elif grocery_opts.mode is "debug_make_grocery_list":
        for i in range(0, len(master_recipe_list)):
            my_grocery_list.add_from_recipe(master_recipe_list[i-1])
        my_grocery_list.write_to_file('DEBUG_grocery_list_'+datetime.datetime.now().strftime('%A_%d-%m-%y_%H-%M')+'.txt', grocery_opts.output_filetype)
    else:
        print(grocery_opts.mode + ' mode not found check in grocery_options.py - exited without saving')