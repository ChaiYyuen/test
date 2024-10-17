import streamlit as st
import requests
import urllib.parse
import base64
import json
from datetime import datetime, timedelta
from random import choice
import string

# Spotify API credentials
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = "https://genresync.streamlit.app/"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


def generate_random_string(length):
  return ''.join(
      choice(string.ascii_letters + string.digits) for _ in range(length))


def get_authorization_url():
  """Construct the Spotify authorization URL."""
  state = generate_random_string(16)
  scope = "user-read-private user-read-email"

  query_params = {
      "response_type": "code",
      "client_id": CLIENT_ID,
      "scope": scope,
      "redirect_uri": REDIRECT_URI,
      "state": state
  }

  # Building the URL for Spotify authorization
  auth_url = AUTH_URL + urllib.parse.urlencode(query_params)
  return auth_url


def get_token(code):
  auth_string = CLIENT_ID + ":" + CLIENT_SECRET
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

  headers = {
      "Authorization": "Basic " + auth_base64,
      "Content-Type": "application/x-www-form-urlencoded"
  }
  data = {
      "grant_type": "authorization_code",
      "code": code,
      "redirect_uri": REDIRECT_URI
  }
  result = requests.post(TOKEN_URL, headers=headers, data=data)
  json_result = json.loads(result.content)
  return json_result


def refresh_token(refresh_token):
  auth_string = CLIENT_ID + ":" + CLIENT_SECRET
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

  headers = {
      "Authorization": "Basic " + auth_base64,
      "Content-Type": "application/x-www-form-urlencoded"
  }
  data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
  result = requests.post(TOKEN_URL, headers=headers, data=data)
  json_result = json.loads(result.content)
  return json_result


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


def get_user_playlists(token):
  url = f"{API_BASE_URL}me/playlists?limit=50"
  headers = get_auth_header(token)
  result = requests.get(url, headers=headers)
  json_result = json.loads(result.content)['items']
  if len(json_result) == 0:
    return None
  return json_result


auth_url = get_authorization_url


def main():
  st.title("Spotify Artist and Playlist Explorer")
  st.write(auth_url)
  # Initialize session state
  if 'token_info' not in st.session_state:
    st.session_state['token_info'] = None
    st.session_state['is_authenticated'] = False
  if 'token_expiry' not in st.session_state:
    st.session_state['token_expiry'] = None

  # Check for OAuth callback
  params = st.query_params  # Adjusted to use the new API
  if "code" in params:
    code = params["code"][0]
    token_info = get_token(code)
    if "access_token" in token_info:
      st.session_state['token_info'] = token_info
      st.session_state['token_expiry'] = datetime.now() + timedelta(
          seconds=token_info['expires_in'])
      st.session_state['is_authenticated'] = True
    else:
      st.error("Failed to get access token")
      st.write(token_info)  # This might give more info about the error
      return

  # Check if token needs refreshing
  if st.session_state['is_authenticated']:
    if datetime.now() >= st.session_state['token_expiry']:
      new_token_info = refresh_token(
          st.session_state['token_info']['refresh_token'])
      if "access_token" in new_token_info:
        st.session_state['token_info'] = new_token_info
        st.session_state['token_expiry'] = datetime.now() + timedelta(
            seconds=new_token_info['expires_in'])
      else:
        st.session_state['is_authenticated'] = False
        st.error("Failed to refresh token")
        st.write(new_token_info)  # This might give more info about the error
        return

  # Main app logic
  if not st.session_state['is_authenticated']:
    if st.button("Login with Spotify"):
      st.write(f"Please login: [Spotify Login]({auth_url})")
  else:
    token = st.session_state['token_info']['access_token']

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
    if st.button("Fetch My Playlists"):
      playlists = get_user_playlists(token)
      if playlists:
        st.write("Your Playlists:")
        for idx, playlist in enumerate(playlists):
          st.write(f"{idx+1}. {playlist['name']}")
      else:
        st.write("No playlists found or unable to access your playlists.")

    if st.button("Logout"):
      st.session_state['is_authenticated'] = False
      st.session_state['token_info'] = None
      st.session_state['token_expiry'] = None


if __name__ == "__main__":
  main()
