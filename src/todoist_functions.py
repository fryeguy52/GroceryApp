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


# ------------------------------------------------------------------ batched web-app submission
def _iter_resources(paged_result):
    """Flatten the SDK's paginated resource results into individual objects."""
    for page in paged_result:
        if isinstance(page, (list, tuple)):
            yield from page
        else:
            yield page


def _resolve_target_ids(api):
    """Fetch projects and sections once and resolve both web-app destinations."""
    projects = list(_iter_resources(api.get_projects()))
    sections = list(_iter_resources(api.get_sections()))
    project_ids = {project.name: project.id for project in projects}
    mental_load_project_id = project_ids.get("The Mental Load")
    # Section names are not globally unique in Todoist. Resolve each section
    # within its intended project so a same-named section elsewhere cannot
    # send tasks to the wrong destination.
    section_ids = {
        (section.project_id, section.name): section.id
        for section in sections
    }

    targets = {
        ("The Mental Load", "Weekly Menu"): (
            mental_load_project_id,
            section_ids.get((mental_load_project_id, "Weekly Menu"))
        ),
        ("The Mental Load", "Shopping"): (
            mental_load_project_id,
            section_ids.get((mental_load_project_id, "Shopping"))
        ),
    }
    for (project_name, section_name), (project_id, section_id) in targets.items():
        if not project_id or not section_id:
            log.error(
                'Could not resolve Todoist project/section "%s" / "%s". '
                'Projects available: %s; sections available: %s',
                project_name, section_name,
                [project.name for project in projects],
                [section.name for section in sections],
            )
            return None
    return targets


def _sync_commands(token, commands):
    """Submit one batch of up to 100 Todoist Sync API commands."""
    import json
    import requests

    if not commands:
        return {}
    if len(commands) > 100:
        raise ValueError("Todoist Sync API batches are limited to 100 commands.")

    response = requests.post(
        "https://api.todoist.com/api/v1/sync",
        headers={"Authorization": f"Bearer {token}"},
        data={"commands": json.dumps(commands)},
        timeout=(5, 45),
    )
    response.raise_for_status()
    payload = response.json()
    statuses = payload.get("sync_status", {})
    for command in commands:
        command_uuid = command["uuid"]
        status = statuses.get(command_uuid)
        if status != "ok":
            log.error("Todoist command %s failed or was not confirmed: %r", command_uuid, status)
    return payload


def _new_command(command_type, args, *, temp_id=None):
    """Build a Sync API command with unique IDs for idempotency and dependencies."""
    import uuid

    command = {
        "type": command_type,
        "uuid": str(uuid.uuid4()),
        "args": args,
    }
    if temp_id is not None:
        command["temp_id"] = temp_id
    return command


def post_menu_to_todoist(recipes: list, grocery_list_by_store_order: list) -> tuple[list, bool]:
    """
    Submit recipe tasks and the grocery checklist using Todoist Sync API batches.

    Recipe tasks are batched together. The grocery parent and its first subtasks
    are created in one batch using a temporary parent ID; larger lists continue
    in batches referencing the confirmed parent ID. Returns (failed_recipe_names,
    grocery_success). Existing single-task functions remain available to the
    desktop app.
    """
    failed_recipes = []
    grocery_success = False

    try:
        from todoist_settings import todoist_API_token
    except ImportError:
        log.error("todoist_settings.py not found — cannot submit menu.")
        return [recipe.get_name() for recipe in recipes], False

    api = _get_api()
    if api is None:
        return [recipe.get_name() for recipe in recipes], False

    try:
        targets = _resolve_target_ids(api)
    except Exception:
        log.exception("Could not resolve Todoist project and section IDs")
        return [recipe.get_name() for recipe in recipes], False
    if targets is None:
        return [recipe.get_name() for recipe in recipes], False

    weekly_project_id, weekly_section_id = targets[("The Mental Load", "Weekly Menu")]
    shopping_project_id, shopping_section_id = targets[("The Mental Load", "Shopping")]

    recipe_commands = []
    recipe_by_uuid = {}
    for recipe in recipes:
        # The Todoist Sync API requires a temp_id for every item_add
        # command, including standalone recipe tasks.
        command = _new_command("item_add", {
            "content": recipe.get_name(),
            "project_id": weekly_project_id,
            "section_id": weekly_section_id,
            "description": recipe.get_instructional_text(),
            "due": {"string": "Today"},
        }, temp_id=str(__import__("uuid").uuid4()))
        recipe_commands.append(command)
        recipe_by_uuid[command["uuid"]] = recipe.get_name()

    for offset in range(0, len(recipe_commands), 100):
        batch = recipe_commands[offset:offset + 100]
        try:
            result = _sync_commands(todoist_API_token, batch)
            statuses = result.get("sync_status", {})
            for command in batch:
                if statuses.get(command["uuid"]) != "ok":
                    failed_recipes.append(recipe_by_uuid[command["uuid"]])
            log.info("Submitted recipe batch: %d task(s).", len(batch))
        except Exception:
            log.exception("Error submitting batched recipe tasks to Todoist")
            failed_recipes.extend(recipe_by_uuid[command["uuid"]] for command in batch)

    grocery_items = [item.strip() for item in grocery_list_by_store_order if item and item.strip()]
    if not grocery_items:
        return failed_recipes, False

    import uuid
    timestamp = datetime.now().strftime("%a %d %b %Y %H:%M")
    parent_name = f"Groceries - {timestamp}"
    parent_temp_id = str(uuid.uuid4())
    parent_command = _new_command("item_add", {
        "content": parent_name,
        "project_id": shopping_project_id,
        "section_id": shopping_section_id,
        "due": {"string": "Today"},
    }, temp_id=parent_temp_id)

    # Keep the parent in the first batch so its temporary ID can be resolved.
    first_commands = [parent_command]
    for item in grocery_items[:99]:
        first_commands.append(_new_command("item_add", {
            "content": item,
            "project_id": shopping_project_id,
            "parent_id": parent_temp_id,
        }, temp_id=str(uuid.uuid4())))

    try:
        result = _sync_commands(todoist_API_token, first_commands)
        statuses = result.get("sync_status", {})
        parent_ok = statuses.get(parent_command["uuid"]) == "ok"
        parent_id = result.get("temp_id_mapping", {}).get(parent_temp_id)
        items_ok = all(statuses.get(command["uuid"]) == "ok" for command in first_commands[1:])

        if parent_ok and parent_id:
            remaining = grocery_items[99:]
            for offset in range(0, len(remaining), 100):
                batch = [
                    _new_command("item_add", {
                        "content": item,
                        "project_id": shopping_project_id,
                        "parent_id": parent_id,
                    }, temp_id=str(uuid.uuid4()))
                    for item in remaining[offset:offset + 100]
                ]
                result_more = _sync_commands(todoist_API_token, batch)
                more_statuses = result_more.get("sync_status", {})
                items_ok = items_ok and all(
                    more_statuses.get(command["uuid"]) == "ok" for command in batch
                )
        else:
            log.error("Todoist did not confirm the grocery parent task or return its ID.")
            items_ok = False

        grocery_success = parent_ok and bool(parent_id) and items_ok
        if grocery_success:
            log.info("Submitted grocery parent and %d subtask(s) to Todoist.", len(grocery_items))
        else:
            log.warning("Todoist grocery submission was only partially confirmed.")
    except Exception:
        log.exception("Error submitting batched grocery list to Todoist")

    return failed_recipes, grocery_success


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
