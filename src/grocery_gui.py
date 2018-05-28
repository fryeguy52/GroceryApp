__author__ = 'Joe'

from appJar import gui
import random
import grocery_functions


def recipeGUI(selected_items):
    ### Load data
    a_list = grocery_functions.get_recipe_names("..\\recipes", ["chicken", "easy"])
    all_recipes ={}
    for item in a_list:
        all_recipes[item] = False

    suggest_recipes = all_recipes.copy()
    menu_recipes = {}
    rand_suggestion = random.choice(list(suggest_recipes))

    ### Configure
    app_title = "Menu Builder"

    section_1_title="All Recepies"
    section_2_title="Random Suggestion"
    section_3_title="Current Menu"

    button_name_add_selected = "Add Selected"
    button_name_new_selection = "New Suggestion"
    button_name_add_selection = "Add Suggestion"
    button_name_no_save_quit = "Quit"
    button_name_remove_items = "Remove Selected"
    button_name_save_quit = "Save and Quit"
    button_7 = "b7"
    button_8 = "b8"

    ### debug constants
    # rand_suggestion = "poo"

    ### Function defs
    def press(button):
        if button == button_name_add_selected:
            add_selected_button_action()
        elif button == button_name_new_selection:
            new_suggest_button_action()
        elif button == button_name_add_selection:
            add_suggestion_button_action()
        elif button == button_name_no_save_quit:
            no_save_quit_button_action()
        elif button == button_name_remove_items:
            remove_items_button_action()
        elif button == button_name_save_quit:
            save_quit_button_action()
        elif button == button_7:
            print(button)
        elif button == button_8:
            print(button)
        else:
            print(button+" is not a recognised button")
            app.stop()


    ###
    def new_suggest_button_action():
        rand_sug = random.choice(list(suggest_recipes))
        app.setLabel(section_2_title, rand_sug)


    def add_suggestion_button_action():
        rand_suggestion = app.getLabel(section_2_title)
        app.setProperty(section_3_title, rand_suggestion)


    def remove_items_button_action():
        current_menu = app.getProperties(section_3_title)
        for item in current_menu:
            if current_menu[item]:
                app.deleteProperty(section_3_title, item)


    def add_selected_button_action():
        all_rec = app.getProperties(section_1_title)
        for item in all_rec:
            if all_rec[item]:
                app.setProperty(section_3_title, item)
                app.setProperty(section_1_title, item, False)

    def no_save_quit_button_action():
        app.stop()

    def save_quit_button_action():
        nonlocal selected_items
        for i in list(app.getProperties(section_3_title)):
            selected_items.append(i)
        app.stop()


    ### initialization look and feel
    app = gui()
    app.setBg("lightBlue")
    app.setFont(12)

    ### add widgets
    # title
    app.addLabel("title", app_title, 0, 0,)
    app.setLabelBg("title", "orange")
    app.addButton(button_name_no_save_quit, press, 4,0)
    app.addButton(button_name_save_quit, press, 4,2)

    # select recipe panel
    app.startScrollPane("Pane1", 1, 0)
    app.addProperties(section_1_title, all_recipes)
    app.stopScrollPane()
    app.addButton(button_name_add_selected, press, 2,0)

    # random suggestion panel
    app.addLabel(section_2_title, rand_suggestion, 1, 1,)
    app.setLabelBg(section_2_title, "orange")
    app.addButtons([button_name_new_selection, button_name_add_selection], press, 2,1)

    # current selection panel
    app.addProperties(section_3_title, menu_recipes, 1,2)
    app.addButton(button_name_remove_items, press, 2,2)

    ### go
    app.go()

if __name__ == "__main__":
    all_recipes = ["Cheese", "Tomato", "Bacon", "Corn", "Mushroom"]
    selected = []
    recipeGUI(all_recipes, selected)
    print(selected)

