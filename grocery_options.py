__author__ = 'Joe'
JTxCan_Albertsons=["bread",
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

MoxTr_Smiths=["bakery",
              "liquor",
              "fruit",
              "root",
              "vegetable",
              "Frozen",
              "tortillas",
              "condiments",
              "bread",
              "international",
              "canned",
              "pasta",
              "baking",
              "spices",
              "meat",
              "cereal",
              "cheese",
              "dairy",
              "juice",
              "soda",
              "snacks"]

EuJt_Smiths=["liquorl",
              "veggies",
              "fruit",
              "root",
              "condiments",
              "snacks",
              "tortillas",
              "candy/sodas",
              "frozen",
              "meat",
              "lunch meat",
              "cheese",
              "dairy",
              "bread",
              "peanut butter",
              "pasta",
              "international",
              "canned",
              "asian food",
              "breakfast",
              "baking"]

class grocery_options:
    def __init__(self):
        self.include_tags=[]
        self.exclude_tags=["hide"]
        self.default_recipes=["Grocery Staples"]
        self.print_order=EuJt_Smiths

        # debug_show_recipe_list
        # debug_make_grocery_list
        # CLI
        #GUI
        self.mode="GUI"
        self.output_filetype="trello"
        self.print_config_vars="no"

    def print_options(self):
        print("options")


