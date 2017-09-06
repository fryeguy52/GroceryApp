__author__ = 'Joe'


class GroceryList:
    def __init__(self, master_ingredient_dict={}):
        self.store_location_list = []
        self.master_ingredient_dict = master_ingredient_dict
        self.needed_grocery_dict = {}
        self.recipes_to_make = []
        self.print_order = []

        for i in self.master_ingredient_dict:
            if self.master_ingredient_dict[i] not in self.store_location_list:
                self.store_location_list.append(self.master_ingredient_dict[i])
        self.store_location_list.sort()

        for loc in self.store_location_list:
            self.needed_grocery_dict[loc] = {}

    def print_to_screen(self):
        print('\n\nGroceries for:')
        for r in self.recipes_to_make:
            print(r)

        for loc in self.needed_grocery_dict:
            print('*******************************************')
            print(loc.upper())
            for i in self.needed_grocery_dict[loc]:
                print('[] '+i, '('+str(self.needed_grocery_dict[loc][i])+')')
            print('[]')
            print('[]')
            print('[]')
            print()

    def write_to_file(self, file_name, output_type='printed_list'):
        f_out=open("../"+file_name,'w')
        f_out.write('Groceries for:\n')
        for r in self.recipes_to_make:
            f_out.write(r + '\n')
        #print(output_type)
        for loc in self.needed_grocery_dict:
            if loc not in self.print_order:
                self.print_order.append(loc)

        if output_type is 'trello':
            # for loc in self.needed_grocery_dict:
            #     # f_out.write(loc.upper()+'\n')
            #     for i in self.needed_grocery_dict[loc]:
            #         f_out.write(loc + ' -- '+i + ' ('+str(self.needed_grocery_dict[loc][i])+')\n')
            for loc in self.print_order:
                # f_out.write(loc.upper()+'\n')
                try:
                    for i in self.needed_grocery_dict[loc]:
                        f_out.write(loc + ' -- '+i + ' ('+str(self.needed_grocery_dict[loc][i])+')\n')
                except:
                    pass
                    # print(loc+" is not a valid location")
        else:
            for loc in self.needed_grocery_dict:
                f_out.write('*******************************************\n')
                f_out.write(loc.upper()+'\n')
                for i in self.needed_grocery_dict[loc]:
                    f_out.write('[] '+i + ' ('+str(self.needed_grocery_dict[loc][i])+')\n')
                f_out.write('[]\n')
                f_out.write('[]\n')
                f_out.write('[]\n')


    def add_from_recipe(self, recipe_to_add):
        self.recipes_to_make.append(recipe_to_add.name)
        for i in recipe_to_add.ingredients:
            if i in self.needed_grocery_dict[self.master_ingredient_dict[i]]:
                self.needed_grocery_dict[self.master_ingredient_dict[i]][i] += 1
            else:
                self.needed_grocery_dict[self.master_ingredient_dict[i]][i] = 1