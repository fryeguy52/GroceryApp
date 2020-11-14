__author__ = 'Joe'
import glob
import datetime
import grocery_gui
import trello_functions


class Ingredient():
    def __init__(self, input_string):
        self.original_input_string=input_string
        self.format_error=""
        self.recipe_name=""
        if len(input_string.split(",")) == 3:
            self.name = input_string.split(",")[2].strip().lower().rstrip("s.")
            self.unit = input_string.split(",")[1].strip().lower().rstrip("s.")
            self.number = input_string.split(",")[0].strip().lower().rstrip("s.")
            if self.name.endswith("oe"):
                self.name = self.name.rstrip("e")
        else:
            self.format_error = "invalid input line: " + input_string
            self.name=self.format_error
            self.unit = self.format_error
            self.number = self.format_error

    def get_name(self):
        return self.name

    def get_unit(self):
        return self.unit

    def get_number(self):
        return self.number


class Recipe():
    """
    currently not used at all

    a list of ingredients, a name, a text field for recipe instructions
    """
    def __init__(self, recipe_file_name):
        # name give to the recipe internally is based on the filename
        self.name = recipe_file_name.split("\\")[-1].rstrip(".txt")

        # the name of the file used to create this recipe
        self.file_name = recipe_file_name

        # the body of the recipe. ie add 1 cup of flour to....
        self.instructional_text = ""

        # a list of ingredient objects
        self.ingredient_list = []

        # a list of strings describing any errors that occured in parsing the file
        self.recipe_file_errors = []

        # list of strings of tags
        self.tags = []

        # a list of strings of each ingredient's name
        self.list_of_ingredient_names=[]

        # indicate ifthis recipe has been selected for use
        # TODO
        self.is_selected=False

        # mark if this recipe is a recipe staples list this will prevent it from posting to trello and being
        # marked with a timestamp
        self.is_grocery_staples_recipe=False
        if "Grocery Staples" in recipe_file_name:
            self.is_grocery_staples_recipe=True

        ### Data about this recipe in relation to other recipes ###
        # recipe.names as key will map to calculated distances
        self.distance_to_recipe_dict={}

        # the average distance from this recipe to any other
        self.average_distance=0

        # any headings other than the ones defined here will give an error
        acceptable_headings = ["tags", "ingredients", "recipe"]

        heading = ''
        with open(recipe_file_name, 'r') as recipe_file:
            for line in recipe_file:
                if line.strip() == '':
                    pass
                elif line[0] == "#":
                    if line.strip("##").strip().lower() in acceptable_headings:
                        heading = line.strip("##").strip()
                    else:
                        self.recipe_file_errors.append(line.strip("##").strip().lower() + " is not a valid heading")
                elif heading.lower() == "ingredients":
                    current_ingredient = Ingredient(line)
                    current_ingredient.recipe_name=self.name
                    self.list_of_ingredient_names.append(current_ingredient.name)
                    self.ingredient_list.append(current_ingredient)
                    if current_ingredient.format_error != "":
                        self.recipe_file_errors.append(current_ingredient.format_error)
                elif heading.lower() == "recipe":
                    self.instructional_text += line
                elif heading.lower() == "tags":
                    self.tags.append(line.strip())
                else:
                    pass

        self.check_for_missing_tags()
        self.sort_ingredient_list()

    def add_ingredient(self, new_ingredient):
        self.ingredient_list.append(new_ingredient)
        self.sort_ingredient_list()

    def add_tag(self, tag):
        self.tags.append(tag)

    def get_name(self):
        return self.name

    def get_instructional_text(self):
        return self.instructional_text

    def get_ingredient_list(self):
        return self.ingredient_list

    def sort_ingredient_list(self):
        self.ingredient_list.sort(key=lambda x: x.name)

    def check_for_missing_tags(self):

        # recipes will be required to contain at least one tag from each of the following sets:

        list_of_tag_sets=[]
        list_of_tag_sets.append(['chicken', 'turkey', 'beef', 'pork', 'fish', 'shrimp', 'vegetarian'])
        list_of_tag_sets.append(['summer', 'fall', 'winter', 'spring'])
        list_of_tag_sets.append(['easy', 'medium', 'hard'])
        list_of_tag_sets.append(['asian', 'italian', 'mexican', 'american', 'indian', 'greek', 'european',
                                   'middle eastern', 'mediterranean'])
        list_of_tag_sets.append(['stove', 'grill', 'oven', 'crock pot', 'instant pot', 'no cooking'])
        list_of_tag_sets.append(['breakfast', 'lunch', 'dinner', 'side'])

        for tag_set in list_of_tag_sets:
            if not any(tag in self.tags for tag in tag_set):
                self.recipe_file_errors.append("Missing one of the following tags: " + str(tag_set))

    def calculate_distance_from_another_recipe(self, other_recipe):
        print_differences=False
        print_differences_lists = False

        set_of_this_recipes_ingredients=set(self.list_of_ingredient_names)
        set_of_this_recipes_tags=set(self.tags)

        set_of_other_recipes_ingredients=set(other_recipe.list_of_ingredient_names)
        set_of_other_recipes_tags = set(self.tags)

        set_of_common_ingredients=set_of_this_recipes_ingredients.intersection(set_of_other_recipes_ingredients)
        set_of_different_ingredients=set_of_this_recipes_ingredients.symmetric_difference(set_of_other_recipes_ingredients)

        set_of_common_tags = set_of_this_recipes_tags.intersection(set_of_other_recipes_tags)
        set_of_different_tags = set_of_this_recipes_tags.symmetric_difference(set_of_other_recipes_tags)

        list_of_common_ingredients=list(set_of_common_ingredients)
        list_of_different_ingredients=set(set_of_different_ingredients)

        list_of_common_tags = list(set_of_common_tags)
        list_of_different_tags = set(set_of_different_tags)

        num_common_ingredients = len(list_of_common_ingredients)
        num_different_ingredients = len(list_of_different_ingredients)
        num_common_tags = len(list_of_common_tags)
        num_different_tags = len(list_of_different_tags)

        percent_common_ingredeints=float(num_common_ingredients/(num_common_ingredients+num_different_ingredients))
        percent_common_tags=float(num_common_tags / (num_common_tags + num_different_tags))
        percent_of_all_things_in_common=float((num_common_ingredients + num_common_tags)/
                                              (num_common_ingredients+num_different_ingredients + num_common_tags + num_different_tags))

        if print_differences:
            print("comparing " +self. name + " and " + other_recipe.name)

            print("common ingredients: " + str(100*percent_common_ingredeints) + "% " + str(num_common_ingredients) +  "/" + str(num_common_ingredients+num_different_ingredients))
            print("common ingredients: " + str(100 * percent_common_tags) + "% " + str(num_common_tags) + "/" + str(num_common_tags + num_different_tags))

            if print_differences_lists:
                print("Common ingredients (" + str(num_common_ingredients) + "): ")
                for ingredient in list_of_common_ingredients:
                    print(ingredient)

                print("Different ingredients (" + str(num_different_ingredients) + "): ")
                for ingredient in list_of_different_ingredients:
                    print(ingredient)

                print("Common tags (" + str(num_common_tags) + "): ")
                for tag in list_of_common_tags:
                    print(tag)

                print("Different tags (" + str(num_different_tags) + "): ")
                for tag in list_of_different_tags:
                    print(tag)

                print("--------------------------------------------------------------")
        self.distance_to_recipe_dict[other_recipe.name] =  1 - percent_of_all_things_in_common
        self.calculate_average_distance()
        return percent_of_all_things_in_common

    def calculate_average_distance(self):
        sum_of_dists=0
        if len(self.distance_to_recipe_dict) > 0:
            for recipe in self.distance_to_recipe_dict:
                sum_of_dists=self.distance_to_recipe_dict[recipe] + sum_of_dists
            self.average_distance = float(sum_of_dists/len(self.distance_to_recipe_dict))
        else:
            self.average_distance=0


class RecipeCollection():
    def __init__(self):
        # a list of Recipe() objects
        self.recipe_list=[]

        # TODO
        self.ingredient_list=[]

        # a list of strings formated like this
        # <ingredient_name>: amount1, unit1, amount2, unit2
        self.grocery_list=[]

        # grocery list above but reordered to match a store configure file
        self.grocery_list_by_store_order=[]

        # a list of stings of the names of the recipes
        self.recipe_names_list=[]

        # a list of strings that describe any format errors from recipe files
        self.recipe_file_format_errors=[]

        # a list strings that is just the names of the ingredients
        self.unique_ingredient_list = []

        # a dictionary taking ingredient namwes as keys and giving out times the ingredient appears in all recipes
        self.ingredient_count_dict={}

    def add_recipe(self, recipe):
        self.recipe_list.append(recipe)

    def get_ingredient_list(self):
        return self.ingredient_list

    def get_grocery_list(self):
        self.make_ingredient_list()
        return self.grocery_list

    def get_grocery_list_by_store_order(self, store_config_file_name):
        self.sort_grocery_list_by_store_order(store_config_file_name)
        return self.grocery_list_by_store_order

    def get_recipe_by_name(self, requested_name):
        for recipe in self.recipe_list:
            if recipe.get_name() == requested_name:
                return recipe
        print(requested_name + " Not Found!")

    def get_recipe_names(self, search_tags=[]):

        recipe_names = []

        if search_tags == []:
            for recipe in self.recipe_list:
                recipe_names.append(recipe.name)
        else:
            for recipe in self.recipe_list:
                if set(search_tags).issubset(recipe.tags):
                    recipe_names.append(recipe.name)

        if recipe_names == []:
            recipe_names.append("No recipes match the tags: " + str(search_tags))

        return recipe_names

    def get_recipe_file_format_errors(self):
        self.collect_recipe_file_format_errors()
        return self.recipe_file_format_errors

    def get_unique_ingredient_list(self):
        self.make_unique_ingredient_list()
        return self.unique_ingredient_list

    def sort_ingredient_list(self):
        self.ingredient_list.sort(key=lambda x: x.name)

    def add_all_recipes_in_dir(self, recipe_dir):
        for file in glob.glob(recipe_dir+"/*.txt"):
            current_recipe=Recipe(file)
            self.recipe_list.append(current_recipe)

    def generate_ingredient_count(self):
        self.ingredient_count_dict={}

        for recipe in self.recipe_list:
            for ingredient in recipe.ingredient_list:
                if ingredient.name in self.ingredient_count_dict:
                    self.ingredient_count_dict[ingredient.name] += 1
                else:
                    self.ingredient_count_dict[ingredient.name] = 1

        for ingredient in self.ingredient_count_dict:
            print(ingredient + ": " + str(self.ingredient_count_dict[ingredient]))

    def make_ingredient_list(self):
        self.ingredient_list=[]
        self.grocery_list=[]

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
                condensed_dict[dict_key] = Ingredient(ingredient.original_input_string)

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

    def make_unique_ingredient_list(self):
        self.unique_ingredient_list = []
        for recipe in self.recipe_list:
            for ingredient in recipe.ingredient_list:
                if not ingredient.name in self.unique_ingredient_list:
                    self.unique_ingredient_list.append(ingredient.name)
        self.unique_ingredient_list.sort()


    def sort_grocery_list_by_store_order(self, store_config_file_name, default_store_file_name):
        self.make_ingredient_list()
        self.grocery_list_by_store_order=[]

        store_specific_output_department_from_ingredient, \
        store_specific_output__ingredient_list_from_department, \
        store_specific_print_order = get_item_dept_dicts_and_print_order_from_store_config_file(store_config_file_name)

        default_output_department_from_ingredient,\
        default_ing_list_from_dept_key, \
        default_print_order = get_item_dept_dicts_and_print_order_from_store_config_file(default_store_file_name)

        # check to see if an item is listed in the non-default store file and will
        # write out items in the the order given in the store config file
        for dept in store_specific_print_order:
            for item in self.grocery_list:
                name_of_grocery_item=item.split(':')[0]
                if name_of_grocery_item in store_specific_output_department_from_ingredient:
                    if store_specific_output_department_from_ingredient[name_of_grocery_item] == dept:
                        self.grocery_list_by_store_order.append(dept + " -- " + item)
                elif name_of_grocery_item in default_output_department_from_ingredient:
                    if default_output_department_from_ingredient[name_of_grocery_item] == dept:
                        self.grocery_list_by_store_order.append(dept + " -- " + item)
                else:
                    self.grocery_list_by_store_order.append("No Department Listed -- " + item)

    def write_store_ordered_grocery_list_to_file(self, file_name):
        if self.grocery_list_by_store_order == []:
            print("grocery_list_by_store_order does not exist yet. skipping.")
        else:
            output_file = open(file_name, "w")
            output_file.write("*** Recipes this Week ***\n")
            for recipe in self.recipe_list:
                output_file.write(recipe.name + "\n")
            output_file.write("*************************\n\n")

            for i in range(0, len(self.grocery_list_by_store_order)):
                output_file.write(self.grocery_list_by_store_order[i]+"\n")

    def collect_recipe_file_format_errors(self):
        self.recipe_file_format_errors=[]
        for recipe in self.recipe_list:
            for error in recipe.recipe_file_errors:
                self.recipe_file_format_errors.append(recipe.name + ": " + error)

    def read_time_stamp_file(self,
                             recipe_time_stamp_file_name,
                             date_for_timedelta=datetime.date.today(),
                             days_for_timedelta=21
                             ):

        recipe_to_time_stamp_dict={}
        with open(recipe_time_stamp_file_name, 'r') as time_stamp_file:
            for line in time_stamp_file:
                recipe_name = line.split(":")[0].strip()
                time_stamp = line.split(":")[1].strip()
                date = datetime.date(int(time_stamp.split("-")[0]),
                                     int(time_stamp.split("-")[1]),
                                     int(time_stamp.split("-")[2]))
                if recipe_name in recipe_to_time_stamp_dict:
                    if date > recipe_to_time_stamp_dict[recipe_name]:
                        recipe_to_time_stamp_dict[recipe_name] = date
                else:
                    recipe_to_time_stamp_dict[recipe_name] = date

            for recipe_name in recipe_to_time_stamp_dict:
                if recipe_name in self.get_recipe_names():
                    if date_for_timedelta - recipe_to_time_stamp_dict[recipe_name] < datetime.timedelta(days=days_for_timedelta):
                        self.get_recipe_by_name(recipe_name).tags.append("recently-used")

        for recipe in self.recipe_list:
            if not "recently-used" in recipe.tags:
                recipe.add_tag("not-recently-used")

    def calculate_recipe_distances(self):
        for recipe in self.recipe_list:
            for other_recipe in self.recipe_list:
                if not recipe.is_grocery_staples_recipe and not other_recipe.is_grocery_staples_recipe:
                    if not recipe.name == other_recipe.name:
                        recipe.calculate_distance_from_another_recipe(other_recipe)

    def print_recipe_distances(self):
        self.calculate_recipe_distances()
        for recipe in self.recipe_list:
            print("---------------------------------------")
            print("Distances from " + recipe.name)
            for recipe_name in recipe.distance_to_recipe_dict:
                print(recipe_name+": "+str(recipe.distance_to_recipe_dict[recipe_name]))


    def write_recipe_usage_data(self, recipe_time_stamp_file_name, mark_recipes_with_this_date=datetime.date.today(),read_or_append='a'):
        with open(recipe_time_stamp_file_name, read_or_append) as time_stamp_file:
            for recipe in self.recipe_list:
                if not recipe.is_grocery_staples_recipe:
                    time_stamp_file.write(recipe.name+": "+str(mark_recipes_with_this_date)+"\n")

    def write_recipe_stats_to_files(self, directory="..\\recipes\\"):
        ingredient_count_sort_by_count_file_name="ing_count_by_count.data"
        ingredient_count_sort_by_name_file_name = "ing_count_by_ing.data"
        recipe_usage_count_sort_by_count="recipe_usage_by_usage.data"
        recipe_usage_count_sort_by_usage="recipe_usage_by_recipe.data"
        recipe_distances_sort_by_difference="dist_by_dist.data"
        recipe_distances_sort_by_recipe="dist_by_recipe.data"
        directory = directory + "data\\"

        self.calculate_recipe_distances()
        with open(directory+recipe_distances_sort_by_recipe, "w") as output_file:
            for recipe in self.recipe_list:
                sorted_distances = sorted(recipe.distance_to_recipe_dict.items(), key=lambda x: x[1], reverse=True)
                output_file.write("\n\n---------------------------------------\n")
                output_file.write("Distances from " + recipe.name+"\n")
                output_file.write("---------------------------------------\n")
                for i in range(0, len(sorted_distances)):
                    output_file.write(sorted_distances[i][0] + ": " + str(sorted_distances[i][1])+"\n")

        with open(directory+recipe_distances_sort_by_difference, "w") as output_file:
            recipe_to_dist_dict={}
            for recipe in self.recipe_list:
                for other_recipe in self.recipe_list:
                    if not recipe.name == other_recipe.name \
                            and not recipe.is_grocery_staples_recipe \
                            and not other_recipe.is_grocery_staples_recipe:
                        if recipe.name > other_recipe.name:
                            recipe_to_dist_dict[recipe.name + " ----> " +
                                                other_recipe.name] = recipe.distance_to_recipe_dict[other_recipe.name]
                        else:
                            recipe_to_dist_dict[recipe.name + " ----> " +
                                                other_recipe.name] = recipe.distance_to_recipe_dict[other_recipe.name]

            sorted_distances = sorted(recipe_to_dist_dict.items(), key=lambda x: x[1], reverse=True)
            for i in range(0, len(sorted_distances)):
                        output_file.write(sorted_distances[i][0] + ": " + str(sorted_distances[i][1])+"\n")




def get_item_dept_dicts_and_print_order_from_store_config_file(file_name):
    """
    return two dictionaries from specified file. one takes itmes
    as keys and returns a department one takes a department as a
    key and returns a list of items
    """
    heading=''
    dept_list_of_ing_dict={}
    ingredient_dept_dict={}
    print_order_list=[]
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

    return ingredient_dept_dict, dept_list_of_ing_dict, print_order_list,


def get_all_ingredients_from_store_config_file(file_name):
    heading=''
    all_ingredients_list=[]
    with open(file_name,'r') as defaultDeptFile:
        for line in defaultDeptFile:
            if line.strip() == '':
                pass
            elif line[0] == "#":
                heading=line.strip("##").strip().lower()
            elif heading == 'print order':
                pass
            else:
                all_ingredients_list.append(line.strip())
    return all_ingredients_list


def get_all_ingredients(recipe_dir, default_item_dept_file_name):
    all_recipes = RecipeCollection()
    all_recipes.add_all_recipes_in_dir(recipe_dir)
    all_ingredients_in_all_recipes = all_recipes.get_unique_ingredient_list()

    #default_item_dept_file_name = "defaultItemDepartments.txt"
    all_ingredients_from_default_dept_file = get_all_ingredients_from_store_config_file(default_item_dept_file_name)

    for ingredient_name in all_ingredients_from_default_dept_file:
        if not ingredient_name in all_ingredients_in_all_recipes:
            all_ingredients_in_all_recipes.append(ingredient_name)

    all_ingredients_in_all_recipes.sort()
    return all_ingredients_in_all_recipes


def update_default_ing_dept_file(input_list, default_Store_File_Name):
    #defaultStoreFileName = "defaultItemDepartments.txt"

    default_dept_from_ing_key, \
    default_ing_list_from_dept_key, \
    print_order = get_item_dept_dicts_and_print_order_from_store_config_file(default_Store_File_Name)

    print_order.sort()
    out_file=open(default_Store_File_Name, "w")
    out_file.write("## print order\n")
    for dept in print_order:
        out_file.write(dept+"\n")

    for dept in print_order:
        out_file.write("\n## "+dept+"\n")
        for item in input_list:
            if item in default_dept_from_ing_key:
                if default_dept_from_ing_key[item] == dept:
                    out_file.write(item+"\n")
            else:
                pass

    for item in input_list:
        if item not in default_dept_from_ing_key:
            out_file.write(item+"\n")

    out_file.close()

def run_trello_grocery_list_app(
        recipe_directory,
        grocery_store_config_file,
        default_store_file_name,
        recipe_time_stamp_file_name,
        grocery_list_output_file_name,
        post_to_trello,
        append_time_stamps
        ):

    update_default_ing_dept_file(get_all_ingredients(recipe_directory, default_store_file_name), default_store_file_name)

    all_of_the_recipes = RecipeCollection()
    all_of_the_recipes.add_all_recipes_in_dir(recipe_directory)
    #all_of_the_recipes.write_recipe_usage_data(recipe_time_stamp_file_name, mark_recipes_with_this_date=datetime.date(2020, 1, 1),read_or_append='w')

    grocery_file_errors=all_of_the_recipes.get_recipe_file_format_errors()

    if grocery_file_errors == []:
        selected_recepes = []
        grocery_gui.recipeGUI(selected_recepes, recipe_directory, recipe_time_stamp_file_name)
        recipes_for_the_week=RecipeCollection()
        recipes_for_the_week.read_time_stamp_file(recipe_time_stamp_file_name)
        for recipe_name in selected_recepes:
            current_recipe = all_of_the_recipes.get_recipe_by_name(recipe_name)
            recipes_for_the_week.add_recipe(current_recipe)
            if post_to_trello and not current_recipe.is_grocery_staples_recipe:
                trello_functions.post_recipe_to_trello(current_recipe)

        recipes_for_the_week.sort_grocery_list_by_store_order(grocery_store_config_file, default_store_file_name)
        recipes_for_the_week.write_store_ordered_grocery_list_to_file(grocery_list_output_file_name)
        if append_time_stamps:
            recipes_for_the_week.write_recipe_usage_data(recipe_time_stamp_file_name)
    else:
        for error in grocery_file_errors:
            print(error)