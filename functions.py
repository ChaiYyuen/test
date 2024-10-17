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
  """
  eg: user["display_name"]
  More on response sample in 
  https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
  """


def get_user_playlists(token):
  url = f"{API_BASE_URL}me/playlists?limit=50"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)
  if len(json_result) == 0:
    return None
  return json_result
  """
  eg: playlist["name"]
  """
