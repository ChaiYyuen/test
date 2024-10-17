from requests import post, get
import json

API_BASE_URL = "https://api.spotify.com/v1/"


def get_auth_header(token):
  return {"Authorization": "Bearer " + token}


def get_user_profile(token):
  url = API_BASE_URL + "me"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_results = json.loads(result.content)
  return json_results
