__author__ = 'Joe'

import random as rand
import datetime

import groceryFileIO
import ingedientTools
import grocery_list


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
    print('*    2) recommend a random recipe to add        *')
    print('*    3) approve and save list                   *')
    print('*    4) quit and discard list                   *')
    print('*                                               *')
    print('*************************************************')


def initialize():
    master_ing_dict = groceryFileIO.read_ingredient_file('master_ingredient_list.json')
    master_recipe_list = groceryFileIO.read_recipe_file('master_recipe_list.json')
    my_grocery_list = grocery_list.GroceryList(master_ing_dict)
    ingedientTools.extract_ingredients(master_recipe_list, master_ing_dict)
    ingedientTools.add_ingredient_locations(master_ing_dict)
    groceryFileIO.write_ingredient_file(master_ing_dict, 'master_ingredient_list.json')

    return master_recipe_list, my_grocery_list


def recommend_random(my_grocery_list, master_recipe_list):
    while True:
        rand_index = rand.randint(0, len(master_recipe_list)-1)
        accept_recipe_choice = input("would you like to eat " + master_recipe_list[rand_index].name + " this week?(y/n)")
        if accept_recipe_choice == 'y':
            my_grocery_list.add_from_recipe(master_recipe_list[rand_index])
            return
        elif accept_recipe_choice == 'n':
            try_another = 'p'
            while try_another != 'n' and try_another != 'y':
                try_another = input("would you like a different suggestion? (y/n)")
                if try_another == 'n':
                    return

def add_specific_recipe(my_grocery_list, master_recipe_list):
    print('\nHere are all of the recipes to choose from:')
    for r in range(0, len(master_recipe_list)):
        print(str(r+1) + ') ' + master_recipe_list[r].name)
    menu_choice = input('enter the number of the recipe you wish to add: ')
    try:
        i = int(menu_choice)
        if i in range(1, len(master_recipe_list)+1):
            my_grocery_list.add_from_recipe(master_recipe_list[i-1])
        else:
            print('invalid menu choice. no recipe added')
    except:
        print('invalid menu choice. no recipe added')

if __name__ == "__main__":
    master_recipe_list, my_grocery_list = initialize()

    continue_flag = True
    while continue_flag:
        print_menu_options(my_grocery_list.recipes_to_make)
        menu_choice = input('select an option from above: ')
        if menu_choice == '1':
            add_specific_recipe(my_grocery_list, master_recipe_list)
        elif menu_choice == '2':
            recommend_random(my_grocery_list, master_recipe_list)
        elif menu_choice == '3':
            print('save not yet implemented')
            continue_flag = False
            my_grocery_list.write_to_file('grocery_list_'+datetime.datetime.now().strftime('%A_%d-%m-%y_%H-%M')+'.txt')
            my_grocery_list.print_to_screen()
        elif menu_choice == '4':
            print('exited without saving')
            continue_flag = False