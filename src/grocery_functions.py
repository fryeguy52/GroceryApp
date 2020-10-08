__author__ = 'Joe'
import re
import glob
import ntpath

class shopping_item():
    number=[]
    unit=[]
    name=[]
    grocery_list_line=[]

class Ingredient():
    """
    Currently unused the idea is to replace code in this file with more OO design
    """
    def __init__(self, input_string):
        if len(input_string.split(",")) == 3:
          self.name   = input_string.split(",")[2].strip().lower().rstrip("s.")
          self.unit   = input_string.split(",")[1].strip().lower().rstrip("s.")
          self.number = input_string.split(",")[0].strip().lower().rstrip("s.")
          if self.name.endswith("oe"):
              self.name = self.name.rstrip("e")
        else:
            self.name = "invalid input line: " + input_string
            self.unit = self.name
            self.number = self.name

    def getName(self):
        return self.name

    def getUnit(self):
        return self.unit

    def getNumber(self):
        return self.number

class Recipe():
    """
    currently not used at all

    a list of ingredients, a name, a text field for recipe instructions
    """
    def __init__(self, recipe_file_name):
        self.name = recipe_file_name.split("\\")[-1].rstrip(".txt")
        self.file_name = recipe_file_name
        self.instructional_text = ""
        self.ingredient_list = []

        heading = ''
        ingredient_list = []
        with open(recipe_file_name, 'r') as recipe_file:
            for line in recipe_file:
                if line.strip() == '':
                    pass
                elif line[0] == "#":
                    heading = line.strip("##").strip()
                elif heading.lower() == "ingredients":
                    current_ingredient = Ingredient(line)
                    self.ingredient_list.append(current_ingredient)
                elif heading.lower() == "recipe":
                    self.instructional_text += line
                else:
                    pass

        self.sort_ingredient_list()

    def add_ingredient(self, new_ingredient):
        self.ingredient_list.append(new_ingredient)
        self.sort_ingredient_list()

    def get_name(self):
        return self.name

    def get_instructional_text(self):
        return self.instructional_text

    def get_ingredient_list(self):
        return self.ingredient_list

    def sort_ingredient_list(self):
        self.ingredient_list.sort(key=lambda x: x.name)

class RecipeCollection():
    def __init__(self):
        self.recipe_list=[]
        self.ingredient_list=[]
        self.grocery_list=[]
        self.recipe_names_list=[]

    def add_recipe(self, recipe):
        self.recipe_list.append(recipe)

    def get_ingredient_list(self):
        return self.ingredient_list

    def get_grocery_list(self):
        return self.grocery_list

    def get_recipe_names(self):
        recipe_names=[]
        for recipe in self.recipe_list:
            recipe_names.append(recipe.name)
        return recipe_names

    def sort_ingredient_list(self):
        self.ingredient_list.sort(key=lambda x: x.name)

    def make_ingredient_list(self):
        self.ingredient_list=[]

        # collect all the ingredients from all the recipes into one list
        for recipe in self.recipe_list:
            for ingredient in recipe.get_ingredient_list():
                self.ingredient_list.append(ingredient)

        condensed_list = []
        condensed_dict = dict()
        for ingredient in self.ingredient_list:
            dict_key = ingredient.unit + "-" + ingredient.name
            if dict_key in condensed_dict:
                condensed_dict[dict_key].number = str(
                    float(condensed_dict[dict_key].number) + float(ingredient.number))
            else:
                condensed_dict[dict_key] = ingredient

        for item in condensed_dict:
            condensed_list.append(condensed_dict[item])

        condensed_list.sort(key=lambda x: x.name)
        condensed_dict = {}
        for item in condensed_list:
            if item.name in condensed_dict:
                condensed_dict[item.name] = condensed_dict[item.name] + ", " + item.number.strip() + " " + item.unit.strip()
            else:
                condensed_dict[item.name] = item.name + ": " + item.number.strip() + " " + item.unit.strip()
        self.grocery_list = []
        for item in condensed_dict:
            self.grocery_list.append(condensed_dict[item])


def get_recipe_names(recipe_dir, search_tags=[]):
    """
    return a list of all the .txt files in a directory without the extension
     this list will represent all the available recipes to the user
    :param recipe_dir: which directory to search
    :return: a list of strings. each is the name of a txt file in recipe_dir
    """
    recipe_names=[]

    if search_tags == []:
        for file in glob.glob(recipe_dir+"/*.txt"):
            head, file = ntpath.split(file)
            file = re.sub('.txt', '', file)
            recipe_names.append(file)
    else:
        for file in glob.glob(recipe_dir+"/*.txt"):
            head, file = ntpath.split(file)
            file = re.sub('.txt', '', file)
            file_tags = get_tags_from_recipe_file(recipe_dir+"/"+file+".txt")
            if(set(search_tags).issubset(file_tags)):
                recipe_names.append(file)

    if recipe_names == []:
        for file in glob.glob(recipe_dir + "/*.txt"):
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
    with open(file, 'r') as recipe_file:
        for line in recipe_file:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip()
            elif heading.lower() == "ingredients":
                current_ingredient=shopping_item()
                current_ingredient.number = line.split(",")[0].strip().lower().rstrip("s.")
                current_ingredient.unit = line.split(",")[1].strip().lower().rstrip("s.")
                current_ingredient.name = line.split(",")[2].strip().lower().rstrip("s.")
                if current_ingredient.name.endswith("oe"):
                    current_ingredient.name = current_ingredient.name.rstrip("e")

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
    with open(file, 'r') as recipe_file:
        for line in recipe_file:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip()
            elif heading.lower() == "tags":
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
    recipe=""
    with open(file, 'r') as recipe_file:
        for line in recipe_file:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip()
            elif heading.lower() == "recipe":
                recipe += line
            else:
                pass
    return recipe

def print_grocery_list(list_of_grocery_items):
    for grocery_item in list_of_grocery_items:
        print(grocery_item.name)

def condense_grocery_list(list_of_grocery_items):
    """
    take a list of grocery items and return a list of grocery items
    where the ones that share a name and unit have been combined by
    incrementing the number
    TODO: implement some kind of unit conversions for popular units
    """
    condensed_list=[]
    condensed_dict=dict()
    for grocery_item in list_of_grocery_items:
        dict_key=grocery_item.unit+"-"+grocery_item.name
        if dict_key in condensed_dict:
            condensed_dict[dict_key].number = str(float(condensed_dict[dict_key].number) + float(grocery_item.number))
        else:
            condensed_dict[dict_key]=grocery_item

    for item in condensed_dict:
        condensed_list.append(condensed_dict[item])

    condensed_list.sort(key=lambda x: x.name)
    condensed_dict={}
    for item in condensed_list:
        if item.name in condensed_dict:
            condensed_dict[item.name] = condensed_dict[item.name] + ", " + item.number.strip() + " " + item.unit.strip()
        else:
            condensed_dict[item.name]=item.name + ": " + item.number.strip() + " " + item.unit.strip()
    condensed_list=[]
    for item in condensed_dict:
        new_item=shopping_item()
        new_item.name=item
        new_item.grocery_list_line=condensed_dict[item]
        condensed_list.append(new_item)

    return condensed_list

def get_item_dept_dicts(file_name='defaultItemDepartments.txt'):
    """
    return two dictionaries from specified file. one takes itmes
    as keys and returns a department one takes a department as a
    key and returns a list of items
    """
    heading=''
    dept_list_of_ing_dict={}
    ingredient_dept_dict={}
    print_order_list=[]
    all_ingredients_list=[]
    with open(file_name,'r') as defaultDeptFile:
        for line in defaultDeptFile:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip().lower()
                if heading =='print order':
                    pass
                else:
                    dept_list_of_ing_dict[heading]=[]
            elif heading == 'print order':
                print_order_list.append(line.strip().lower())
            else:
                dept_list_of_ing_dict[heading].append(line.strip())
                ingredient_dept_dict[line.strip()]=heading
                all_ingredients_list.append(line.strip())

    return ingredient_dept_dict, dept_list_of_ing_dict, print_order_list, all_ingredients_list

def get_all_ingredients(recipe_dir="..//recipes"):
    recipe_names = get_recipe_names(recipe_dir)
    all_ingredients_in_all_recipes=[]
    for recipe in recipe_names:
        all_ingredients_in_all_recipes += get_ingredients_from_recipe_file(recipe_dir+"\\"+recipe+".txt")
    for ingredient in all_ingredients_in_all_recipes:
        ingredient.unit=''


    default_item_dept_file_name = "defaultItemDepartments.txt"
    default_dept_from_ing_key, default_ing_list_from_dept_key, print_order, all_ingredients_from_default_dept_file = get_item_dept_dicts(default_item_dept_file_name)
    for ingredient_name in all_ingredients_from_default_dept_file:
        current_ingredient = shopping_item()
        current_ingredient.number = '0'
        current_ingredient.unit = ''
        current_ingredient.name = ingredient_name.strip().lower().rstrip("s.")
        all_ingredients_in_all_recipes.append(current_ingredient)

    grocery_list=condense_grocery_list(all_ingredients_in_all_recipes)
    return grocery_list

def update_default_ing_dept_file(input_list):
    input_list.sort(key=lambda x: x.name)
    defaultStoreFileName = "defaultItemDepartments.txt"
    default_dept_from_ing_key, default_ing_list_from_dept_key, print_order, all_ingredients_from_default_dept_file = get_item_dept_dicts(defaultStoreFileName)
    print_order.sort()
    out_file=open(defaultStoreFileName, "w")
    out_file.write("## print order\n")
    for dept in print_order:
        out_file.write(dept+"\n")

    for dept in print_order:
        out_file.write("\n## "+dept+"\n")
        for item in input_list:
            if item.name in default_dept_from_ing_key:
                if default_dept_from_ing_key[item.name] == dept:
                    out_file.write(item.name+"\n")
            else:
                pass

    #out_file.write("\n## NO DEPARTMENT!\n")
    for item in input_list:
        if item.name not in default_dept_from_ing_key:
            out_file.write(item.name+"\n")

    out_file.close()

def sort_and_print_grocery_list_file(recipe_list, grocery_list, StoreCofigFileName=""):
    output_file_name="..//most_recent_grocery_list.txt"
    defaultStoreFileName = "defaultItemDepartments.txt"
    default_dept_from_ing_key, default_ing_list_from_dept_key, print_order, all_ingredients_from_default_dept_file  = get_item_dept_dicts(defaultStoreFileName)
    out_file=open(output_file_name,"w")

    # write the list of recipes to file
    out_file.write("*** Recipes this Week ***\n")
    for recipe in recipe_list:
        out_file.write(recipe+"\n")
    out_file.write("*************************\n\n")

    if StoreCofigFileName != "":
        dict_dept_from_ing_key, dict_ing_list_from_dept_key, print_order, all_ingredients_from_default_dept_file  = get_item_dept_dicts(StoreCofigFileName)
    else:
        dict_dept_from_ing_key={}
        dict_ing_list_from_dept_key={}

    # check to see if an item is listed in the non-default store file and will
    # write out items in the the order given in the store config file
    for dept in print_order:
        for item in grocery_list:
            if item.name in dict_dept_from_ing_key:
                if dict_dept_from_ing_key[item.name] == dept:
                    out_file.write(dept + " -- " + item.grocery_list_line+"\n")
            elif item.name in default_dept_from_ing_key:
                if default_dept_from_ing_key[item.name] == dept:
                    out_file.write(dept + " -- " + item.grocery_list_line+"\n")
            else:
                pass

    for item in grocery_list:
        if item.name not in dict_dept_from_ing_key and item.name not in default_dept_from_ing_key:
            out_file.write("No Department Listed -- " + item.grocery_list_line+"\n")

    pass

def check_recipe_format(recipe_dir="..//recipes", verbose=True):

    # any headings other than the ones defined here will give an error
    acceptable_headings=["tags", "ingredients", "recipe"]

    # recipes will be required to contain at least one tag from each of the following sets:
    required_tag_set_meat   = ['chicken', 'turkey', 'beef', 'pork', 'fish', 'shrimp', 'vegetarian']
    required_tag_set_season = ['summer', 'fall', 'winter', 'spring']
    required_tag_set_effort = ['easy', 'medium', 'hard']
    required_tag_set_region = ['asian', 'italian', 'mexican', 'american', 'indian', 'greek', 'european', 'middle eastern', 'mediterranean']
    required_tag_set_method = ['stove', 'grill', 'oven', 'crock pot', 'instant pot', 'no cooking']
    required_tag_set_when   = ['breakfast', 'lunch', 'dinner', 'side']

    # recipes will be encouraged to contain at least one tag from each of the following sets:
    required_tag_set_category = ['pasta', 'casserole', 'sandwich']


    recipe_names = get_recipe_names(recipe_dir)
    tmp=""
    errors=[]
    for recipe in recipe_names:
        file=recipe_dir+"//"+recipe+".txt"
        heading=''
        ingredient_list=[]
        all_tags_list=[]
        with open(file,'r') as recipe_file:
            recipe_text=get_recipe_from_recipe_file(file)
            if recipe_text == []:
                error_string="Blank recipe in: "+file
                if verbose:
                    print(error_string)
                errors.append(error_string)

            # check each linein the file
            # if it is empty, then ignore
            # if it starts with a '#' then check that a valid heading follows and set variable "heading" to new value
            # if the new line is not blank or a heading change then switch based on heading:
            # the ingredient heading needs to be formatted correctly in terms of comma separated values
            # the tags need to have members of certain tags lists. ie each recipe must have one of :[chicken. beef, vegitarian, etc...]
            for line in recipe_file:
                if line.strip() == '':
                    pass
                elif line[0] == "#":
                    heading=line.strip("##").strip().lower()
                    if heading not in acceptable_headings:
                        error_string = "invalid heading, \""+heading+"\" in file: "+file
                        if verbose:
                            print(error_string)
                        errors.append(error_string)
                elif heading == "ingredients":
                    try:
                        tmp = line.split(",")[0]
                        tmp = line.split(",")[1]
                        tmp = line.split(",")[2]
                        if len(line.split(",")) > 3:
                            error_string="invalid format, \""+line.strip()+"\" in: "+file
                            if verbose:
                                print(error_string)
                            errors.append(error_string)
                    except IndexError:
                        error_string="invalid format, \""+line.strip()+"\" in: "+file
                        if verbose:
                            print(error_string)
                        errors.append(error_string)
                elif heading == "tags":
                    all_tags_list.append(line.strip())
                else:
                    pass
            errors_from_missing_tags(file, required_tag_set_meat, all_tags_list, errors)
            errors_from_missing_tags(file, required_tag_set_season, all_tags_list, errors)
            errors_from_missing_tags(file, required_tag_set_effort, all_tags_list, errors)
            errors_from_missing_tags(file, required_tag_set_region, all_tags_list, errors)
            errors_from_missing_tags(file, required_tag_set_method, all_tags_list, errors)
            errors_from_missing_tags(file, required_tag_set_when, all_tags_list, errors)

    return errors

def no_common_member(list_a=[], list_b=[]):
# if the two list have at least one member in common then return false
# else true
    if list_a == []:
        return True
    if list_b == []:
        return True
    for i in list_a:
        if i in list_b:
            return False
    return True

def errors_from_missing_tags(file, list_required_tags=[], list_all_tags=[], errors=[]):
    if no_common_member(list_required_tags, list_all_tags):
        error_string = file + " is missing a tag from the following set: " + str(list_required_tags) + str(list_all_tags)
        print(error_string)
        errors.append(error_string)
        pass