"""
trello_functions.py
-------------------
Trello integration: posts selected recipes as cards to the
"House" board → "This Week" list via the Trello REST API.

Credentials are loaded from trello_settings.py (not committed to git).
See trello_settings.example.py for the required variables.
"""

__author__ = 'Joe'

import requests


def post_recipe_to_trello(recipe):
    """Post a Recipe object as a card to the Trello "This Week" list."""
    from trello_settings import trello_token, trello_key

    base = 'https://trello.com/1/'
    auth = {'key': trello_key, 'token': trello_token}

    # Find the "House" board
    boards = requests.get(base + 'members/me/boards', params=auth).json()
    house_board = next((b for b in boards if b['name'] == 'House'), None)
    if not house_board:
        print('Error: "House" board not found on Trello.')
        return

    # Find the "This Week" list on that board
    lists = requests.get(base + f'boards/{house_board["id"]}/lists', params=auth).json()
    this_week = next((lst for lst in lists if lst['name'] == 'This Week'), None)
    if not this_week:
        print('Error: "This Week" list not found on the House board.')
        return

    requests.post(base + 'cards', params=auth, data={
        'name':   recipe.get_name(),
        'desc':   recipe.get_instructional_text(),
        'idList': this_week['id'],
    })
