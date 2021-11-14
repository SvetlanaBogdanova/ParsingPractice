import requests
import json
from pprint import pprint

# Выведем заголовки статей из результатов поиска New York Times по слову Russia
api_key = ''
url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
params = {'q': 'Russia', 'api-key': api_key}

response = requests.get(url, params=params)
j_data = json.loads(response.text)
pprint([doc['headline']['main'] for doc in j_data['response']['docs']])

with open("nyt_search_result.json", "w") as file:
    json.dump(j_data, file, indent=4)
