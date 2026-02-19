"""
todoist_functions.py
--------------------
Todoist integration: posts selected recipes as tasks to the
"The Mental Load" project → "Weekly Menu" section.

Credentials are loaded from todoist_settings.py (not committed to git).
See todoist_settings.example.py for the required variables.
"""

__author__ = 'Joe'

from todoist_api_python.api import TodoistAPI


def post_recipe_to_todoist(recipe):
    """Add a Recipe as a task in Todoist under the Weekly Menu section."""
    from todoist_settings import todoist_API_token

    api = TodoistAPI(todoist_API_token)
    target_project = 'The Mental Load'
    target_section = 'Weekly Menu'

    try:
        projects = api.get_projects()
        for proj in projects:
            for p in proj:
                 if p.name == target_project:
                    project_id = p.id
        if not project_id:
            print(f'Error: project "{target_project}" not found.')
            return
        sections = api.get_sections()
        for sect in sections:
            for s in sect:
                if s.name == target_section:
                    section_id = s.id
        if not section_id:
            print(f'Error: section "{target_section}" not found.')
            return

        api.add_task(
            content=recipe.get_name(),
            project_id=project_id,
            section_id=section_id,
            description=recipe.get_instructional_text(),
            due_string='Today',
        )
    except Exception as error:
        print(f'Todoist error: {error}')

def post_grocery_list_to_todoist(grocerlist):
    """Add a Recipe as a task in Todoist under the Weekly Menu section."""
    from todoist_settings import todoist_API_token

    api = TodoistAPI(todoist_API_token)
    target_project = 'The Mental Load'
    target_section = 'Weekly Menu'

    try:
        projects = api.get_projects()
        for proj in projects:
            for p in proj:
                 if p.name == target_project:
                    project_id = p.id
                                        
        if not project_id:
            print(f'Error: project "{target_project}" not found.')
            return
        
        sections = api.get_sections()
        for sect in sections:
            for s in sect:
                if s.name == target_section:
                    section_id = s.id
                                    
        if not section_id:
            print(f'Error: section "{target_section}" not found.')
            return

        api.add_task(
            content=recipe.get_name(),
            project_id=project_id,
            section_id=section_id,
            description=recipe.get_instructional_text(),
            due_string='Today',
        )
    except Exception as error:
        print(f'Todoist error: {error}')
