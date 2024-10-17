import streamlit as st
import requests
import urllib.parse
import base64
import json
from datetime import datetime, timedelta

import functions as func
import interface as ui

# Spotify API credentials
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = "https://genresync.streamlit.app/"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"


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


def main():
  # Initialize session state
  ui.initialiser()
  if 'token_info' not in st.session_state:
    st.session_state['token_info'] = None
    st.session_state['is_authenticated'] = False
  if 'token_expiry' not in st.session_state:
    st.session_state['token_expiry'] = None
  if 'callback_processed' not in st.session_state:
    st.session_state['callback_processed'] = False

  # Check for OAuth callback
  params = st.query_params  # Adjusted to use the new API
  if "code" in params and not st.session_state['callback_processed']:
    code = params["code"]
    token_info = get_token(code)
    if "access_token" in token_info:
      st.session_state['token_info'] = token_info
      st.session_state['token_expiry'] = datetime.now() + timedelta(
          seconds=token_info['expires_in'])
      st.session_state['is_authenticated'] = True
      st.session_state[
          'callback_processed'] = True  # Mark callback as processed
    else:
      st.error("Failed to get access token")
      st.write(token_info)  # This might give more info about the error
      return
  elif 'error' in params:
    st.rerun()

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
    auth_params = {
        "response_type": 'code',
        "client_id": CLIENT_ID,
        "scope": "user-read-private user-read-email playlist-read-private",
        "redirect_uri": REDIRECT_URI,
        "show_dialog": True
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
    ui.login_page(auth_url)
  else:
    token = st.session_state['token_info']['access_token']

    st.session_state['logged_in'] = True
    st.session_state['page'] = 'main'

    #User Profile
    user_profile = func.get_user_profile(token)
    playlists = func.get_user_playlists(token)
    ui.set_username(user_profile['display_name'])
    ui.set_playlist(playlists)
    ui.page_selector()

    if not st.session_state["logged_in"]:
      st.session_state['is_authenticated'] = False
      st.session_state['token_info'] = None
      st.session_state['token_expiry'] = None
      st.rerun()


if __name__ == "__main__":
  main()
