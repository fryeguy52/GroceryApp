__author__ = 'Joe'

class grocery_options:
    def __init__(self):
        self.include_tags=[]
        self.exclude_tags=["hide"]
        self.default_recipes=["Grocery Staples"]
        self.print_order=["bread",
                          "crackers",
                          "meat",
                          "alcohol",
                          "cheese",
                          "tortillas",
                          "soda",
                          "frozen",
                          "coffee",
                          "cereal",
                          "baking",
                          "canned",
                          "soup",
                          "pasta",
                          "chips",
                          "international",
                          "condiments",
                          "spices",
                          "dairy",
                          "root",
                          "vegetable",
                          "fruit",
                          "produce"]

        # debug_show_recipe_list
        # debug_make_grocery_list
        # normal
        self.mode="normal"
        self.output_filetype="trello"
        self.print_config_vars="no"

    def print_options(self):
        print("options")


