import streamlit as st
import requests
import urllib.parse
import base64
import json
from datetime import datetime, timedelta

# Spotify API credentials
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = "https://genresync.streamlit.app/callback"  # Update this to your Streamlit app URL

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


def get_token():
  auth_string = CLIENT_ID + ":" + CLIENT_SECRET
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

  headers = {
      "Authorization": "Basic " + auth_base64,
      "Content-Type": "application/x-www-form-urlencoded"
  }
  data = {"grant_type": "client_credentials"}
  result = requests.post(TOKEN_URL, headers=headers, data=data)
  json_result = json.loads(result.content)
  token = json_result["access_token"]
  return token


def get_auth_header(token):
  return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
  url = API_BASE_URL + "search"
  headers = get_auth_header(token)
  query = f"?q={artist_name}&type=artist&limit=1"
  query_url = url + query
  result = requests.get(query_url, headers=headers)
  json_result = json.loads(result.content)["artists"]["items"]
  if len(json_result) == 0:
    return None
  return json_result[0]


def get_songs_by_artist(token, artist_id):
  url = f"{API_BASE_URL}artists/{artist_id}/top-tracks?market=US"
  headers = get_auth_header(token)
  result = requests.get(url, headers=headers)
  json_result = json.loads(result.content)["tracks"]
  return json_result


def get_user_playlists(token, user_id):
  url = f"{API_BASE_URL}users/{user_id}/playlists?offset=0&limit=50&locale=en-US"
  headers = get_auth_header(token)
  result = requests.get(url, headers=headers)
  json_result = json.loads(result.content)['items']
  if len(json_result) == 0:
    return None
  return json_result


def main():
  st.title("Spotify Artist and Playlist Explorer")

  # Check if the user is already authenticated
  if 'access_token' not in st.session_state:
    if st.button("Login with Spotify"):
      auth_params = {
          "response_type": 'code',
          "client_id": CLIENT_ID,
          "scope": "user-read-private user-read-email playlist-read-private",
          "redirect_uri": REDIRECT_URI,
          "show_dialog": True
      }
      auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
      st.write(f"Please login: [Spotify Login]({auth_url})")

    params = st.experimental_get_query_params()
    if 'code' in params:
      code = params['code'][0]
      token_info = get_token()
      st.session_state['access_token'] = token_info
      st.experimental_rerun()
  else:
    token = st.session_state['access_token']

    # Artist search
    artist_name = st.text_input("Enter an artist name")
    if artist_name:
      artist = search_for_artist(token, artist_name)
      if artist:
        st.write(f"Artist found: {artist['name']}")
        st.image(artist['images'][0]['url'] if artist['images'] else None,
                 width=200)

        if st.button("Get Top Tracks"):
          songs = get_songs_by_artist(token, artist['id'])
          for idx, song in enumerate(songs):
            st.write(f"{idx+1}. {song['name']}")

    # User playlist fetch
    user_id = st.text_input("Enter a Spotify user ID to fetch playlists")
    if user_id:
      playlists = get_user_playlists(token, user_id)
      if playlists:
        st.write("User's Playlists:")
        for idx, playlist in enumerate(playlists):
          st.write(f"{idx+1}. {playlist['name']}")
      else:
        st.write("No playlists found or unable to access user's playlists.")

    if st.button("Logout"):
      for key in list(st.session_state.keys()):
        del st.session_state[key]
      st.experimental_rerun()


if __name__ == "__main__":
  main()
