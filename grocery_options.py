__author__ = 'Joe'

class grocery_options:
    def __init__(self):
        self.include_tags=[]
        self.exclude_tags=["hide"]
        self.default_recipes=["Grocery Staples"]
        self.mode="normal"
        self.output_filetype="trello"
        self.print_config_vars="no"

    def print_options(self):
        print("""
        self.include_tags=["a", "b"]
        self.include_tags=["c", "d"]
        self.default_recipes=[]
        self.mode="normal"
        self.output_filetype="trello"
        self.print_config_vars="no"
        """)


