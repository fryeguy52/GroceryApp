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
    :param file: a recipe .txt file to extract ingredient information from
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


def matches(string1='', string2=''):
    """
    check to see if string1 and string2 refer to the same grocery store item
    :return True/False
    """

    string1=string1.lower().strip()
    string2=string2.lower().strip()

    if string1 is string2:
        return True

    if string1 == string2:
        return True

    if string1=='' and string2 == '':
        return True

    if string1 is None and string2 is None:
        return True

    if string1.rstrip('.s') == string2.rstrip('.s'):
        return True

    return False

def print_grocery_list(list_of_grocery_items):
    for grocery_item in list_of_grocery_items:
        # print(grocery_item.number+":"+grocery_item.unit+":"+grocery_item.name)
        print(grocery_item.name)

def condense_grocery_list(list_of_grocery_items):
    condensed_list=[]
    condensed_dict=dict()
    for grocery_item in list_of_grocery_items:
        dict_key=grocery_item.unit.strip().lower().rstrip("s.")+"-"+grocery_item.name.strip().lower().rstrip("s.")
        if dict_key in condensed_dict:
            condensed_dict[dict_key].number = str(float(condensed_dict[dict_key].number) + float(grocery_item.number))
        else:
            condensed_dict[dict_key]=grocery_item

    for item in condensed_dict:
        condensed_list.append(condensed_dict[item])

    condensed_list.sort(key=lambda x: x.name)
    # print_grocery_list(condensed_list)
    print(len(list_of_grocery_items), len(condensed_list))

    return condensed_list
