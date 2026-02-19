"""
todoist_functions.py
--------------------
Todoist integration:
  1. post_recipe_to_todoist()    — posts each selected recipe as a task
  2. post_grocery_list_to_todoist() — posts the sorted grocery list as a
     parent task "Groceries - <datetime>" with each item as a subtask

Credentials are loaded from todoist_settings.py (not committed to git).
See todoist_settings.example.py for the required variables.

All output goes to BOTH stdout AND todoist_errors.log (next to this file)
so errors are never silently lost when there's no terminal window.
"""

__author__ = 'Joe'

import logging
import sys
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------ logging
_LOG_FILE = Path(__file__).parent / "todoist_errors.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("todoist")


# ------------------------------------------------------------------ helpers
def _get_api():
    """Return an authenticated TodoistAPI instance, or None on failure."""
    try:
        from todoist_settings import todoist_API_token
    except ImportError:
        log.error("todoist_settings.py not found — copy todoist_settings.example.py and fill in your token.")
        return None
    try:
        from todoist_api_python.api import TodoistAPI
        return TodoistAPI(todoist_API_token)
    except ImportError:
        log.error("todoist-api-python is not installed. Run: pip install todoist-api-python")
        return None


def _resolve_project_and_section(api, target_project: str, target_section: str):
    """Return (project_id, section_id) or (None, None) on failure."""
    try:
        projects = api.get_projects()
        for proj in projects:
            for p in proj:
                if p.name == target_project:
                    project_id = p.id
        if not project_id:
            log.error(f'Project "{target_project}" not found. '
                      f'Available: {[p.name for p in projects]}')
            return None, None

        sections = api.get_sections()
        for sect in sections:
            for s in sect:
                if s.name == target_section:
                    section_id = s.id
        if not section_id:
            log.error(f'Section "{target_section}" not found. '
                      f'Available: {[s.name for s in sections]}')
            return None, None

        return project_id, section_id
    except Exception:
        log.exception("Error resolving Todoist project/section")
        return None, None


# ------------------------------------------------------------------ public API
def post_recipe_to_todoist(recipe) -> bool:
    """
    Add *recipe* as a task in the Weekly Menu section of The Mental Load.
    Returns True on success, False on any failure.
    """
    api = _get_api()
    if api is None:
        return False

    project_id, section_id = _resolve_project_and_section(
        api, "The Mental Load", "Weekly Menu"
    )
    if not project_id:
        return False

    log.info(f"Posting recipe '{recipe.get_name()}' to Todoist …")
    try:
        task = api.add_task(
            content=recipe.get_name(),
            project_id=project_id,
            section_id=section_id,
            description=recipe.get_instructional_text(),
            due_string="Today",
        )
        log.info(f"  ✓ Recipe task created  id={task.id}")
        return True
    except Exception:
        log.exception(f"Error posting recipe '{recipe.get_name()}'")
        return False


def post_grocery_list_to_todoist(grocery_list_by_store_order: list) -> bool:
    """
    Post the sorted grocery list to Todoist.

    Creates a parent task:
        "Groceries - Mon 23 Jun 2025 14:32"
    then adds each item in *grocery_list_by_store_order* as a subtask,
    preserving the store-aisle order.

    Lines look like:  "produce -- apple: 3"
    Subtask content:  "produce -- apple: 3"   (posted as-is, easy to read)

    Returns True if the parent task and all subtasks were created successfully.
    """
    if not grocery_list_by_store_order:
        log.warning("Grocery list is empty — nothing to post.")
        return False

    api = _get_api()
    if api is None:
        return False

    project_id, section_id = _resolve_project_and_section(
        api, "The Mental Load", "Shopping"
    )
    if not project_id:
        return False

    # Parent task name includes date + time so multiple runs don't collide
    timestamp = datetime.now().strftime("%a %d %b %Y %H:%M")
    parent_name = f"Groceries - {timestamp}"

    log.info(f"Creating parent task '{parent_name}' …")
    try:
        parent_task = api.add_task(
            content=parent_name,
            project_id=project_id,
            section_id=section_id,
            due_string="Today",
        )
        log.info(f"  ✓ Parent task created  id={parent_task.id}")
    except Exception:
        log.exception("Error creating parent grocery task")
        return False

    # Add each grocery item as a subtask
    success = True
    for item in grocery_list_by_store_order:
        item = item.strip()
        if not item:
            continue
        try:
            api.add_task(
                content=item,
                project_id=project_id,
                parent_id=parent_task.id,
            )
            log.debug(f"    + subtask: {item}")
        except Exception:
            log.exception(f"Error adding subtask: {item!r}")
            success = False

    if success:
        log.info(f"  ✓ All {len(grocery_list_by_store_order)} items posted as subtasks.")
    else:
        log.warning("Some subtasks failed — check log for details.")

    return success
