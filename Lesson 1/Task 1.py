import requests
import json
from pprint import pprint

username = "octocat"
url = f"https://api.github.com/users/{username}/repos"

response = requests.get(url)
repos_info = json.loads(response.text)

repos_list = [repo['name'] for repo in repos_info]
pprint(repos_list)

with open("github_repos.json", "w") as file:
    json.dump(repos_info, file, indent=4)
