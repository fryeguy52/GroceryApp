__author__ = 'Joe'

from todoist_settings import todoist_API_token
from todoist_api_python.api import TodoistAPI
import grocery_functions

def post_recipe_to_todoist(recipe):
    name = recipe.get_name()
    description = recipe.get_instructional_text()

    api = TodoistAPI(todoist_API_token)
    target_project_name = "Home"
    target_project_id = ""
    target_section_name = "Weekly Menu"
    target_section_id = ""

    try:
        todoist_projects = api.get_projects()
        print(todoist_projects)
        for project in todoist_projects:
            if project.name == target_project_name:
                target_project_id = project.id
        if target_project_id == "":
            print("Error project ", target_project_name, " not found")

        todoist_sections = api.get_sections()
        print(todoist_sections)
        for section in todoist_sections:
            # print(section.name, "  ", section.id, "", section.project_id)
            if section.name == target_section_name:
                target_section_id = section.id
        if target_section_id == "":
            print("Error section ", target_section_name, " not found")

        print(target_project_name, " Project Id = ", target_project_id)
        print(target_section_name, " Section Id = ", target_section_id)

    except Exception as error:
        print(error)

    try:
        task = api.add_task(
            content=recipe.get_name(),
            project_id=target_project_id,
            section_id=target_section_id,
            description=recipe.get_instructional_text(),
            due_string="Today")
        print(task)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    api = TodoistAPI(todoist_API_token)
    target_project_name = "Home"
    target_project_id = ""
    target_section_name = "Weekly Menu"
    target_section_id = ""

    print("Running todoist_functions.py directly")
    print("API Key: ", todoist_API_token)

    try:
        todoist_projects = api.get_projects()
        print(todoist_projects)
        for project in todoist_projects:
            if project.name == target_project_name:
                target_project_id = project.id
        if target_project_id == "":
            print("Error project ", target_project_name," not found")

        todoist_sections = api.get_sections()
        print(todoist_sections)
        for section in todoist_sections:
            #print(section.name, "  ", section.id, "", section.project_id)
            if section.name == target_section_name:
                target_section_id = section.id
        if target_section_id == "":
            print("Error section ", target_section_name, " not found")

        print(target_project_name, " Project Id = ", target_project_id)
        print(target_section_name, " Section Id = ", target_section_id)

    except Exception as error:
        print(error)

    try:
        task = api.add_task(
            content="Test Task added automatically",
            project_id=target_project_id,
            section_id=target_section_id,
            description="Test Description",
            due_string="Today")
        print(task)
    except Exception as error:
        print(error)

