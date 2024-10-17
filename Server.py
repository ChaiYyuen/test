import streamlit as st
import requests
import urllib.parse
from datetime import datetime, timedelta

# Spotify API credentials
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = "https://genresync.streamlit.app/"  # Default Streamlit local URL

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


def get_token(code):
  req_body = {
      'code': code,
      'grant_type': 'authorization_code',
      'redirect_uri': REDIRECT_URI,
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
  }
  response = requests.post(TOKEN_URL, data=req_body)
  token_info = response.json()
  return token_info


def refresh_token(refresh_token):
  req_body = {
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token,
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
  }
  response = requests.post(TOKEN_URL, data=req_body)
  new_token_info = response.json()
  return new_token_info


def get_playlists(access_token):
  headers = {"Authorization": f"Bearer {access_token}"}
  response = requests.get(API_BASE_URL + "me/playlists", headers=headers)
  return response.json()


def main():
  st.title("Spotify Playlist Viewer")

  # Check if the user is already authenticated
  if 'access_token' not in st.session_state:
    # If not authenticated, show the login button
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

    # Check if the authentication code is in the URL
    params = st.experimental_get_query_params()
    if 'code' in params:
      code = params['code'][0]
      token_info = get_token(code)
      st.session_state['access_token'] = token_info['access_token']
      st.session_state['refresh_token'] = token_info['refresh_token']
      st.session_state['token_expiry'] = datetime.now() + timedelta(
          seconds=token_info['expires_in'])
      st.experimental_rerun()

  else:
    # Check if the token needs refreshing
    if datetime.now() >= st.session_state['token_expiry']:
      new_token_info = refresh_token(st.session_state['refresh_token'])
      st.session_state['access_token'] = new_token_info['access_token']
      st.session_state['token_expiry'] = datetime.now() + timedelta(
          seconds=new_token_info['expires_in'])

    # Fetch and display playlists
    playlists = get_playlists(st.session_state['access_token'])
    for playlist in playlists['items']:
      st.write(
          f"**{playlist['name']}** - {playlist['tracks']['total']} tracks")

    if st.button("Logout"):
      for key in list(st.session_state.keys()):
        del st.session_state[key]
      st.experimental_rerun()


if __name__ == "__main__":
  main()
