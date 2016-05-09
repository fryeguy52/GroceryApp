__author__ = 'Joe'

import grocery_list
import recipe
import ingedientTools
import groceryFileIO as grocFileIO

def test_1():
    print('Test_01: Simple ingredient IO')
    test_ingredient_dict={}
    test_ingredient_dict['eggs']='dairy'
    test_ingredient_dict['beef']='meat'

    grocFileIO.write_ingredient_file(test_ingredient_dict, 'test_ing_dict.json')
    new_ing_dict=grocFileIO.read_ingredient_file('test_ing_dict.json')

    if new_ing_dict['eggs'] == 'dairy' and new_ing_dict['beef'] == 'meat':
        print('.................................................................................................. pass')
    else:
        print('.................................................................................................. fail')
    print()

def test_2():
    print('Test_02: Simple recipe IO')
    recipe_list=[]
    recipe1= recipe.Recipe()
    recipe1.name='soup'
    recipe1.ingredients=['water', 'meat', 'veggies']
    recipe1.difficulty='easy'
    recipe_list.append(recipe1)

    recipe2= recipe.Recipe()
    recipe2.name='sandwich'
    recipe2.ingredients=['bread', 'meat', 'cheese']
    recipe2.difficulty='medium'
    recipe_list.append(recipe2)

    grocFileIO.write_recipe_file(recipe_list, 'test_recipes.json')
    new_recipe_list = grocFileIO.read_recipe_file('test_recipes.json')

    original_recipe_names = {}
    for r in recipe_list:
        original_recipe_names[r.name]=''

    match_flag = True

    for r in new_recipe_list:
        match_flag = match_flag and (r.name in original_recipe_names)

    if match_flag:
        print('.................................................................................................. pass')
    else:
        print('.................................................................................................. fail')
    print()

def test_3():
    print('Test_02: Create/augment ingredient list from recipe file')
    recipe_list=[]
    recipe1= recipe.Recipe()
    recipe1.name='soup'
    recipe1.ingredients=['water', 'meat', 'veggies']
    recipe1.difficulty='easy'
    recipe_list.append(recipe1)

    recipe2= recipe.Recipe()
    recipe2.name='sandwich'
    recipe2.ingredients=['bread', 'meat', 'cheese']
    recipe2.difficulty='medium'
    recipe_list.append(recipe2)

    grocFileIO.write_recipe_file(recipe_list, 'test_recipes.json')
    new_recipe_list = grocFileIO.read_recipe_file('test_recipes.json')

    test_ingredient_dict={}
    test_ingredient_dict['eggs']='dairy'
    test_ingredient_dict['beef']='meat'

    ingedientTools.extract_ingredients(new_recipe_list, test_ingredient_dict)
    grocFileIO.write_ingredient_file(test_ingredient_dict, 'ing_test_file.json')
    #print(test_ingredient_dict)

    if 'bread' in test_ingredient_dict and 'water' in test_ingredient_dict and 'eggs' in test_ingredient_dict:
        print('.................................................................................................. pass')
    else:
        print('.................................................................................................. fail')
    print()

def test_4():
    ing_dict = grocFileIO.read_ingredient_file('ing_test_file.json')
    ingedientTools.add_ingredient_locations(ing_dict)
    grocFileIO.write_ingredient_file(ing_dict, 'ing_dict_withj_locations.json')

def test_5():
    ing_dict = grocFileIO.read_ingredient_file('ing_dict_withj_locations.json')
    recipe_list = grocFileIO.read_recipe_file('recipes.json')
    new_grocery_list = grocery_list.GroceryList(ing_dict)
    for r in recipe_list:
        new_grocery_list.add_from_recipe(r)
    new_grocery_list.print_to_screen()

if __name__ == "__main__":
    # test_1()
    # test_2()
    # test_3()
    # test_4()
    test_5()