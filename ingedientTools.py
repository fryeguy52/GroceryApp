__author__ = 'Joe'

import recipe


def extract_ingredients(recipe_list, ingredient_dict={}):
    for o in recipe_list:
        if not isinstance(o, recipe.Recipe):
            print("WARNING! object: "+ o + " is not of Recipe type")
            print(type(o))
            print(o)
            print(recipe_list)
            return
    for r in recipe_list:
        for i in r.ingredients:
            if i not in ingredient_dict:
                ingredient_dict[i]=''

    return ingredient_dict

def add_ingredient_locations(ingredient_dict):
    # print(ingredient_dict)
    location_list=[]
    for i in ingredient_dict:
        if ingredient_dict[i] not in location_list:
            location_list.append(ingredient_dict[i])
    location_list.sort()

    for i in ingredient_dict:
        if ingredient_dict[i] == '':
            stay_in_loop = True
            while stay_in_loop:
                print("\n***************************************")
                print("ingredient "+i+" has no location!")
                for j in range(1, len(location_list)):
                    print (str((j)) + ') ' + location_list[j])
                user_in = input("select a section of the store for " + i + " (enter the number, or type a name for new): ")
                try:
                    num = int(user_in)
                    if num in range(1, len(location_list)):
                        ingredient_dict[i]=location_list[num]
                        stay_in_loop = False
                    else:
                        print('input out of range!')
                except:
                    ingredient_dict[i]=user_in
                    location_list.append(str(user_in))
                    location_list.sort()
                    stay_in_loop = False

    # print(ingredient_dict)
