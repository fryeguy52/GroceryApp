__author__ = 'Joe'

import json

import recipe


def read_ingredient_file(filename):
    with open(filename, 'r') as fp:
        ingredients = json.load(fp)
    return ingredients

def read_recipe_file(filename):

    with open(filename, 'r') as infile:
        new_dict = json.load(infile)

    recipe_list=[]
    for entry in new_dict:
        r = recipe.Recipe()
        r.__dict__ = new_dict[entry][0]
        recipe_list.append(r)
    recipe_list=sorted(recipe_list, key=lambda recipe: recipe.name)

    return recipe_list

def read_options_file():
    options={}
    return options

def write_ingredient_file(ingredient_dict, file_name):
    #write to file
    with open(file_name, 'w') as fp:
        json.dump(ingredient_dict, fp, sort_keys=True, indent=4)

def write_recipe_file(recipe_list, file_name):
    #write to file
    temp_dict={}
    for recipe in recipe_list:
        temp_dict[recipe.name]=[recipe.__dict__]

    with open(file_name, 'w') as outfile:
            json.dump(temp_dict, outfile, sort_keys=True, indent=4)

def write_options_file():
    default_file_name = ''
    write_options_file(default_file_name)

def write_options_file(file_name):
    pass