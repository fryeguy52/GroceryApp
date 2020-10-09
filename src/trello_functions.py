__author__ = 'Joe'

# from trello import TrelloApi
import requests
import grocery_functions
from trello_settings import trello_token
from trello_settings import trello_key

def post_recipe_to_trello(recipe):
    token=trello_token
    key=trello_key

    base = 'https://trello.com/1/'

    boards_url = base + 'members/me/boards'
    params_key_and_token = {'key':key,'token':token}
    arguments = {'fields': 'name', 'lists': 'open'}

    response = requests.get(boards_url, params=params_key_and_token, data=arguments)
    response_array_of_dict = response.json()

    for board in response_array_of_dict:
      if board['name'] == 'House':
        lists_url = base + '/boards/'+board['id']+'/lists'
        list_response=requests.get(lists_url, params=params_key_and_token)
        response_array_of_dict=list_response.json()
        for i in response_array_of_dict:
            if i["name"] == "This Week":
                id_list=i["id"]

        name = recipe.get_name()
        description = recipe.get_instructional_text()
        arguments = {'name': name,
                     'desc': description,
                     'idList' : id_list}

        cards_url= base + 'cards'
        response = requests.post(cards_url, params=params_key_and_token, data=arguments)


if __name__ == "__main__":
    post_recipe_to_trello("Cobb Salad")