__author__ = 'Joe'

import random as rand
import datetime

import groceryFileIO
import ingedientTools
import grocery_list
import grocery_options as GO
import copy

def print_menu_options(current_list):
    print('\n\n\n')
    print('*************************************************')
    print('CURRENT LIST:')
    print()
    if len(current_list) < 1:
        print('EMPTY')
    else:
        for i in range(0, len(current_list)):
            print(str(i+1) + ') ' + current_list[i])
    print()
    print('*************************************************')
    print('*                                               *')
    print('*    1) add a specific recipe to this list      *')
    print('*    2) add a specific recipe with tag          *')
    print('*    3) recommend a random recipe to add        *')
    print('*    4) approve and save list                   *')
    print('*    q) quit and discard list                   *')
    print('*                                               *')
    print('*************************************************')

def filter_recipe_list_from_options(master_recipe_list, grocery_opts: GO.grocery_options):
    filtered_list=[]
    if len(grocery_opts.include_tags) > 0:
        for recipe_from_master in master_recipe_list:
            for tag in grocery_opts.include_tags:
                if tag in recipe_from_master.tags:
                    filtered_list.append(recipe_from_master)
                    break
    else:
        filtered_list = copy.copy(master_recipe_list)

    if len(grocery_opts.exclude_tags) > 0:
        for each_recipe in reversed(filtered_list):
            for tag in grocery_opts.exclude_tags:
                if tag in each_recipe.tags:
                    filtered_list.remove(each_recipe)

    if len(filtered_list) is 0:
        print("WARNING: no recipes on the list.  check the include_tags and exclude_tags in grocery_options.py")

    return filtered_list

def filter_recipe_list_from_tag(master_recipe_list, string_tag, grocery_opts):
    option_filtered_list=filter_recipe_list_from_options(master_recipe_list, grocery_opts)
    filtered_list=[]
    for recipe_from_master in option_filtered_list:
        if string_tag in recipe_from_master.tags:
            filtered_list.append(recipe_from_master)

    if len(filtered_list) is 0:
        print("no recipes with that tag")
        return option_filtered_list

    return filtered_list

def add_defaults(recipe_list, grocery_list : grocery_list.GroceryList, grocery_opts : GO.grocery_options):
    for recipe in recipe_list:
        if recipe.name in grocery_opts.default_recipes:
            grocery_list.add_from_recipe(recipe)
    return

def initialize():
    grocery_opts=GO.grocery_options()
    master_ing_dict = groceryFileIO.read_ingredient_file('master_ingredient_list.json')
    master_recipe_list = groceryFileIO.read_recipe_file('master_recipe_list.json')
    my_grocery_list = grocery_list.GroceryList(master_ing_dict)
    my_grocery_list.print_order=grocery_opts.print_order
    ingedientTools.extract_ingredients(master_recipe_list, master_ing_dict)
    ingedientTools.add_ingredient_locations(master_ing_dict)
    groceryFileIO.write_ingredient_file(master_ing_dict, 'master_ingredient_list.json')

    add_defaults(master_recipe_list, my_grocery_list, grocery_opts)
    # master_recipe_list=filter_recipe_list_from_options(master_recipe_list, grocery_opts)

    return master_recipe_list, my_grocery_list, grocery_opts


def recommend_random(my_grocery_list, master_recipe_list):
    while True:
        rand_index = rand.randint(0, len(master_recipe_list)-1)
        print("would you like to eat " + master_recipe_list[rand_index].name + " this week?")
        accept_recipe_choice = input("(a) yes and another (y) yes and go to menu (n) no but suggest another (q) no and go to menu")
        if accept_recipe_choice == 'y':
            my_grocery_list.add_from_recipe(master_recipe_list[rand_index])
            return
        elif accept_recipe_choice == 'a':
            my_grocery_list.add_from_recipe(master_recipe_list[rand_index])
        elif accept_recipe_choice == 'q':
            return
        elif accept_recipe_choice == 'n':
            pass
        else:
            print("Invalid choice.")

def add_specific_recipe(my_grocery_list, master_recipe_list):
    if len(master_recipe_list) is 0:
        print('\nNo recipes to choose from')
        return

    print('\nHere are all of the recipes to choose from:')
    for r in range(0, len(master_recipe_list)):
        print(str(r+1) + ') ' + master_recipe_list[r].name)
    menu_choice = input('enter the number of the recipe you wish to add (q to quit): ')
    if menu_choice is 'q':
        return

    try:
        i = int(menu_choice)
        if i in range(1, len(master_recipe_list)+1):
            my_grocery_list.add_from_recipe(master_recipe_list[i-1])
        else:
            print('invalid menu choice. no recipe added')
    except:
        print('invalid menu choice. no recipe added')

if __name__ == "__main__":
    master_recipe_list, my_grocery_list, grocery_opts = initialize()
    if grocery_opts.print_config_vars is "yes":
        grocery_opts.print_options()

    if grocery_opts.mode is "normal":
        continue_flag = True
        while continue_flag:
            print_menu_options(my_grocery_list.recipes_to_make)
            menu_choice = input('select an option from above: ')
            if menu_choice == '1':
                add_specific_recipe(my_grocery_list, filter_recipe_list_from_options(master_recipe_list, grocery_opts))
            elif menu_choice == '2':
                tag_string = input('enter tag to: ')
                add_specific_recipe(my_grocery_list, filter_recipe_list_from_tag(master_recipe_list, tag_string, grocery_opts))
            elif menu_choice == '3':
                recommend_random(my_grocery_list, master_recipe_list)
            elif menu_choice == '4':
                print('save not yet implemented')
                continue_flag = False
                my_grocery_list.write_to_file('grocery_list_'+datetime.datetime.now().strftime('%A_%d-%m-%y_%H-%M')+'.txt', grocery_opts.output_filetype)
                my_grocery_list.print_to_screen()
                groceryFileIO.write_recipe_file(master_recipe_list, 'master_recipe_list.json')
            elif menu_choice == 'q':
                print('exited without saving')
                continue_flag = False
    elif grocery_opts.mode is "debug_show_recipe_list":
        master_recipe_list = filter_recipe_list_from_tag(master_recipe_list, "beef")
        for each_recipe in master_recipe_list:
            print(each_recipe.name)
    elif grocery_opts.mode is "debug_make_grocery_list":
        for i in range(0, len(master_recipe_list)):
            my_grocery_list.add_from_recipe(master_recipe_list[i-1])
        my_grocery_list.write_to_file('DEBUG_grocery_list_'+datetime.datetime.now().strftime('%A_%d-%m-%y_%H-%M')+'.txt', grocery_opts.output_filetype)
    else:
        print(grocery_opts.mode + ' mode not found check in grocery_options.py - exited without saving')