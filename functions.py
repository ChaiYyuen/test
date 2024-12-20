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


def get_public_user_playlists(token, id):
  url = f"{API_BASE_URL}users/{id}/playlists"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)
  if len(json_result) == 0:
    return None
  return json_result


def create_user_playlist(token, id, playlist_name, playlist_desc, public):
  url = API_BASE_URL + "users/{id}/playlists"
  headers = get_auth_header(token)
  headers['Content-Type'] = "application/json"
  data = {
      "name": "New Playlist",
      "description": "New playlist description",
      "public": False
  }
  result = post(url, headers=headers, data=data)
  json_result = json.loads(result.content)
  return json_result


def get_user_playlists_items(token, id):
  url = f"{API_BASE_URL}playlists/{id}/tracks"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)
  if len(json_result) == 0:
    return None
  return json_result['items']


def search_for_artist(token, artist_name):
  url = API_BASE_URL + "search"
  headers = get_auth_header(token)
  query = f"?q={artist_name}&type=artist&limit=1"
  query_url = url + query
  result = get(query_url, headers=headers)
  json_result = json.loads(result.content)["artists"]["items"]
  if len(json_result) == 0:
    return None
  return json_result[0]


def get_artist_genre(token, artist_id):
  url = API_BASE_URL + f"artists/{artist_id}"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)['genres']
  if (len(json_result)) == 0:
    return None
  return json_result


def get_songs_by_artist(token, artist_id):
  url = f"{API_BASE_URL}artists/{artist_id}/top-tracks?market=US"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)["tracks"]
  return json_result
