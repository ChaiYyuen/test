import streamlit as st
import requests
import urllib.parse
import base64
from random import choice
import string
from datetime import datetime, timedelta

# Spotify API credentials
CLIENT_ID = "12b02816ea4a4038a6a383cef22a93d7"
CLIENT_SECRET = "3e36ad4cf75a4cda9aea62808f65b921"
REDIRECT_URI = "http://localhost:8501/"

AUTH_URL = "https://accounts.spotify.com/authorize?"
TOKEN_URL = "https://accounts.spotify.com/api/token"


def generate_random_string(length):
    return ''.join(
        choice(string.ascii_letters + string.digits) for _ in range(length))


def get_authorization_url():
    state = generate_random_string(16)
    scope = "user-read-private user-read-email"

    query_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }

    auth_url = AUTH_URL + urllib.parse.urlencode(query_params)

    return auth_url


def exchange_code_for_token(code):
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def refresh_spotify_token(refresh_token):
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to refresh token.')
        return None


def main():
    st.title("Spotify OAuth Integration with Streamlit")

    # Initialize session state
    if 'token_info' not in st.session_state:
        st.session_state['token_info'] = None
        st.session_state['token_expiry'] = None
        st.session_state['is_authenticated'] = False

    # Check if token needs refreshing
    if st.session_state['is_authenticated']:
        if datetime.now() >= st.session_state['token_expiry']:
            new_token_info = refresh_spotify_token(
                st.session_state['token_info']['refresh_token'])
            if new_token_info:
                st.session_state['token_info'] = new_token_info
                st.session_state['token_expiry'] = datetime.now() + timedelta(
                    seconds=new_token_info['expires_in'])
            else:
                st.session_state['is_authenticated'] = False

    # Main app logic
    if not st.session_state['is_authenticated']:
        if st.button("Login with Spotify"):
            auth_url = get_authorization_url()
            st.write(auth_url)
            st.write(f"[Click here to login to Spotify]({auth_url})")

        # Retrieve and store the authorization code from the URL
        if 'code' in st.query_params:  # Replacing st.experimental_get_query_params with st.query_params
            code = st.query_params['code'][0]
            token_info = exchange_code_for_token(code)
            if token_info:
                st.session_state['token_info'] = token_info
                st.session_state['token_expiry'] = datetime.now() + timedelta(
                    seconds=token_info['expires_in'])
                st.session_state['is_authenticated'] = True
            else:
                st.error(
                    "Failed to authenticate. Please try logging in again.")
    else:
        # Display tokens (avoid displaying sensitive tokens in production!)
        st.write("Access Token:",
                 st.session_state['token_info']['access_token'])
        st.write("Refresh Token:",
                 st.session_state['token_info']['refresh_token'])

        if st.button("Logout"):
            st.session_state['is_authenticated'] = False
            st.session_state['token_info'] = None
            st.session_state['token_expiry'] = None


if __name__ == "__main__":
    main()
