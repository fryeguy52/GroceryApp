__author__ = 'Joe'
import re
import glob
import ntpath

class shopping_item():
    number=[]
    unit=[]
    name=[]

def get_recipe_names(recipe_dir):
    """
    return a list of all the .txt files in a directory without the extension
     this list will represent all the available recipes to the user
    :param recipe_dir: which directory to search
    :return: a list of strings. each is the name of a txt file in recipe_dir
    """
    recipe_names=[]
    for file in glob.glob(recipe_dir+"/*.txt"):
        head, file = ntpath.split(file)
        file = re.sub('.txt', '', file)
        recipe_names.append(file)
    return recipe_names

def get_ingredients_from_recipe_file(file):
    """
    return the ingredient information from a recipe file in the form of a list of shopping_item
    objects
    :param file: a recipe .txt file to extract indredient information from
    :return: a list of shopping_item objects. one for each line in the recipe section of the file
    """
    heading=''
    ingredient_list=[]
    with open(file,'r') as recipe_file:
        for line in recipe_file:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip()
            elif heading == "Ingredients":
                current_ingredient=shopping_item()
                current_ingredient.number = line.split(",")[0].strip()
                current_ingredient.unit = line.split(",")[1].strip()
                current_ingredient.name = line.split(",")[2].strip()
                ingredient_list.append(current_ingredient)
            else:
                pass
    return ingredient_list

def get_tags_from_recipe_file(file):
    """
    return the tag information from a recipe file in the form of a list
    :param file: a recipe .txt file to extract indredient information from
    :return: a list of tags
    """
    heading=''
    tag_list=[]
    with open(file,'r') as recipe_file:
        for line in recipe_file:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip()
            elif heading == "Tags":
                tag_list.append(line.strip())
            else:
                pass
    return tag_list

def get_recipe_from_recipe_file(file):
    """
    :param file: a recipe .txt file to extract indredient information from
    :return: a list of lines from the recipe
    """
    heading=''
    recipe=[]
    with open(file,'r') as recipe_file:
        for line in recipe_file:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip()
            elif heading == "Recipe":
                recipe.append(line.strip('\n'))
            else:
                pass
    return recipe