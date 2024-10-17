import streamlit as st
import requests
import urllib.parse
import base64
import json
from datetime import datetime, timedelta

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
    return result.json()

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
    return result.json()

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def main():
    # Initialize session state variables
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
        st.session_state.token_info = None
        st.session_state.token_expiry = None

    # Handle OAuth callback
    params = st.query_params
    if "code" in params and not st.session_state.is_authenticated:
        code = params["code"][0]
        token_info = get_token(code)

        if "access_token" in token_info:
            st.session_state.token_info = token_info
            st.session_state.token_expiry = datetime.now() + timedelta(seconds=token_info['expires_in'])
            st.session_state.is_authenticated = True
            st.experimental_set_query_params()  # Clear query params to avoid re-triggering callback
        else:
            st.error("Failed to get access token")
            st.write(token_info)  # For error diagnostics
            return

    # If authenticated, refresh token if needed
    if st.session_state.is_authenticated:
        if datetime.now() >= st.session_state.token_expiry:
            new_token_info = refresh_token(st.session_state.token_info['refresh_token'])
            if "access_token" in new_token_info:
                st.session_state.token_info = new_token_info
                st.session_state.token_expiry = datetime.now() + timedelta(seconds=new_token_info['expires_in'])
            else:
                st.error("Failed to refresh token")
                st.write(new_token_info)  # For error diagnostics
                st.session_state.is_authenticated = False
                return

    st.title("Spotify Artist and Playlist Explorer")

    # Main app logic if authenticated
    if st.session_state.is_authenticated:
        token = st.session_state.token_info['access_token']

        # Artist search
        artist_name = st.text_input("Enter an artist name")
        if artist_name:
            # Implement search_for_artist and display logic here
            st.write(f"Searching for artist: {artist_name}")
            # Dummy output: Replace with actual implementation
            st.write("Artist found: Example Artist")
            # etc...

        # Logout option
        if st.button("Logout"):
            st.session_state.is_authenticated = False
            st.session_state.token_info = None
            st.session_state.token_expiry = None

    else:
        if st.button("Login with Spotify"):
            auth_params = {
                "response_type": 'code',
                "client_id": CLIENT_ID,
                "scope": "user-read-private user-read-email playlist-read-private",
                "redirect_uri": REDIRECT_URI
            }
            auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(auth_params)}"
            st.write(f"[Login with Spotify]({auth_url})")

if __name__ == "__main__":
    main()