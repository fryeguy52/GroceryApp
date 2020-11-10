__author__ = 'Joe'

import grocery_functions


if __name__ == "__main__":
    grocery_functions.run_trello_grocery_list_app(
        recipe_directory="..\\recipes",
        grocery_store_config_file="JT_Alb.txt",
        default_store_file_name="defaultItemDepartments.txt",
        recipe_time_stamp_file_name="..\\recipe_time_stamps.tmstmp",
        grocery_list_output_file_name="..\\most_recent_grocery_list.txt",
        post_to_trello=True,
        append_time_stamps=True
    )
