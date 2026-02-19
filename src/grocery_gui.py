"""
grocery_gui.py
--------------
GUI layer for the Menu Builder window, built with appJar.

FIX: Circular import removed. Instead of importing grocery_functions and
re-instantiating RecipeCollection internally, this module now receives a
pre-built RecipeCollection as a parameter. The caller (grocery_functions.py)
is responsible for loading data; the GUI is responsible only for display.
"""

__author__ = 'Joe'

import random
from appJar import gui


def recipeGUI(selected_items: list, recipe_collection, recipe_time_stamp_file_name: str = ''):
    """
    Display the Menu Builder window.

    Parameters
    ----------
    selected_items : list
        Output list — recipe names chosen by the user are appended here.
    recipe_collection : RecipeCollection
        A fully loaded RecipeCollection (with timestamps already applied).
        The GUI no longer constructs this itself.
    recipe_time_stamp_file_name : str
        Kept for API compatibility; no longer used inside the GUI.
    """
    filter_tag_list = []
    a_list = recipe_collection.get_recipe_names(filter_tag_list)
    all_recipes = {item: False for item in a_list}
    suggest_recipes = all_recipes.copy()
    menu_recipes = {}
    rand_suggestion = random.choice(list(suggest_recipes))

    # --- Labels / button names ---
    app_title           = 'Menu Builder'
    section_1_title     = 'Recipes'
    section_2_title     = 'Random Suggestion'
    section_3_title     = 'Current Menu'
    section_4_title     = 'Search by Tag'

    BTN_ADD_SELECTED  = 'Add Selected'
    BTN_NEW_SUGGEST   = 'New Suggestion'
    BTN_ADD_SUGGEST   = 'Add Suggestion'
    BTN_FILTER        = 'Filter Recipes'
    BTN_QUIT          = 'Quit'
    BTN_REMOVE        = 'Remove Selected'
    BTN_SAVE_QUIT     = 'Save and Quit'
    BTN_SHOW_RECENT   = 'Show recently used'

    def press(button):
        dispatch = {
            BTN_ADD_SELECTED: _add_selected,
            BTN_NEW_SUGGEST:  _new_suggestion,
            BTN_ADD_SUGGEST:  _add_suggestion,
            BTN_QUIT:         _quit,
            BTN_REMOVE:       _remove_items,
            BTN_SAVE_QUIT:    _save_quit,
            BTN_FILTER:       _filter_recipes,
        }
        action = dispatch.get(button)
        if action:
            action()
        else:
            print(f'{button} is not a recognised button')

    def _new_suggestion():
        app.setLabel(section_2_title, random.choice(list(suggest_recipes)))

    def _add_suggestion():
        suggestion = app.getLabel(section_2_title)
        app.setProperty(section_3_title, suggestion)

    def _remove_items():
        for item, checked in app.getProperties(section_3_title).items():
            if checked:
                selected_items.remove(item)
                app.deleteProperty(section_3_title, item)

    def _filter_recipes():
        tags = app.getEntry(section_4_title).split()
        recipe_list = recipe_collection.get_recipe_names(tags)
        filtered = {item: False for item in recipe_list}
        for item in list(app.getProperties(section_1_title)):
            app.deleteProperty(section_1_title, item)
        app.setProperties(section_1_title, filtered)

    def _add_selected():
        for item, checked in app.getProperties(section_1_title).items():
            if checked:
                unique_item = item
                while unique_item in selected_items:
                    unique_item += '*'
                selected_items.append(unique_item)
                app.setProperty(section_3_title, unique_item)
                app.setProperty(section_1_title, item.strip('*'), False)

    def _quit():
        app.stop()

    def _save_quit():
        nonlocal selected_items
        for i in range(len(selected_items)):
            selected_items[i] = selected_items[i].strip('*')
        app.stop()

    # --- Build UI ---
    app = gui()
    app.setBg('lightBlue')
    app.setFont(12)

    app.addLabel('title', app_title, 0, 0)
    app.setLabelBg('title', 'orange')
    app.addButton(BTN_QUIT,      press, 4, 0)
    app.addButton(BTN_SAVE_QUIT, press, 4, 2)

    app.addEntry(section_4_title, 1, 0, 1, 1)
    app.startScrollPane('Pane1', 2, 0)
    app.addProperties(section_1_title, all_recipes)
    app.stopScrollPane()
    app.addButtons([BTN_ADD_SELECTED, BTN_SHOW_RECENT, BTN_FILTER], press, 3, 0)

    app.addLabel(section_2_title, rand_suggestion, 1, 1)
    app.setLabelBg(section_2_title, 'orange')
    app.addButtons([BTN_NEW_SUGGEST, BTN_ADD_SUGGEST], press, 2, 1)

    app.addProperties(section_3_title, menu_recipes, 1, 2)
    app.addButton(BTN_REMOVE, press, 2, 2)

    app.go()
