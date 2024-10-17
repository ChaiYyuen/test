import streamlit as st
import base64


def initialiser():
  if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

  if 'messages' not in st.session_state:
    st.session_state['messages'] = []

  if 'chatbox_visible' not in st.session_state:
    st.session_state['chatbox_visible'] = False

  if 'page' not in st.session_state:
    st.session_state['page'] = 'main'


# Custom CSS for Spotify theme and chatbox
def css():
  st.markdown("""
      <style>
          body {
              background-color: #121212;
              color: white;
          }
          .title {
              font-size: 50px;
              color: #1DB954;
              text-align: left;
              font-weight: bold;
              font-family: 'Arial', sans-serif;
              text-align: center;
          }
          .subtitle {
              font-family: 'Arial', Helvetica, sans-serif;
              font-size: 30px;
              color: white;
              text-align: center;
              margin-top: 50px;
          }
          .text-input::placeholder {
              color: #888;
          }
          .divider {
              margin-top: 30px;
              margin-bottom: 30px;
              border: 1px solid #1DB954;
          }
  
          .chatbox {
              position: fixed;
              bottom: 80px;
              right: 20px;
              width: 300px;
              height: 400px;
              background-color: #282828;
              border: 1px solid #1DB954;
              border-radius: 10px;
              display: flex;
              flex-direction: column;
              z-index: 1000;
          }
          .chatbox-header {
              background-color: #1DB954;
              color: white;
              padding: 10px;
              border-top-left-radius: 10px;
              border-top-right-radius: 10px;
              font-size: 20px;
              font-weight: bold;
          }
          .chatbox-body {
              flex-grow: 1;
              padding: 10px;
              overflow-y: auto;
              color: white;
              font-size: 14px;
          }
          .chatbox-input {
              display: flex;
              padding: 10px;
          }
          .chatbox-input input {
              flex-grow: 1;
              padding: 5px;
              border: none;
              border-radius: 5px 0 0 5px;
              background-color: #333;
              color: white;
              font-size: 14px;
          }
          .chatbox-input button {
              padding: 5px 10px;
              border: none;
              border-radius: 0 5px 5px 0;
              background-color: #1DB954;
              color: white;
              font-size: 14px;
              cursor: pointer;
          }
  """,
              unsafe_allow_html=True)


# image_loader.py
def render_image(filepath: str):
  """
   filepath: path to the image. Must have a valid file extension.
   """
  mime_type = filepath.split('.')[-1:][0].lower()
  with open(filepath, "rb") as f:
    content_bytes = f.read()
  content_b64encoded = base64.b64encode(content_bytes).decode()
  image_string = f'data:image/{mime_type};base64,{content_b64encoded}'
  st.image(image_string)


def login_page(auth_url):
  css()
  st.markdown(
      "<div class='title'>GenreSync: Tune in to Musical Diversity</div>",
      unsafe_allow_html=True)
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
  left_co, cent_co, last_co = st.columns(3)
  with cent_co:
    render_image("pic/Spotify.png")
  st.markdown('<p class="subtitle">Log in to your Spotify account!</p>',
              unsafe_allow_html=True)
  # Spotify Login Button (Mock login functionality)
  col1, col2, col3 = st.columns([1.3, 1, 1.1])
  col2.link_button('Log in with Spotify', auth_url, type='primary')


def sidebar(username):
  css()
  # Display the user picture at the top of the sidebar
  # st.sidebar.image(userpicture, width=100)
  st.session_state['username'] = username
  st.sidebar.title("Navigation")
  st.sidebar.write(f"Welcome, {st.session_state['username']}!")

  if st.sidebar.button('Log out'):
    st.session_state['logged_in'] = False
    st.session_state['messages'] = []  # Clear chat messages
    st.session_state['chatbox_visible'] = False
    st.session_state['page'] = 'main'  # Reset page on logout

  else:
    st.sidebar.markdown('---')

    # Use a selectbox to persist the state across reruns
    page_selection = st.sidebar.selectbox(
        "Select a page",
        ("Main page", "View Playlists", "Get Song Recommendations",
         "Analyze Genres", "Chat with the Bot"))

    # Set session state page based on selection
    if page_selection == "View Playlists":
      st.session_state['page'] = 'view_playlists'
    elif page_selection == "Get Song Recommendations":
      st.session_state['page'] = 'get_song_recommendations'
    elif page_selection == "Analyze Genres":
      st.session_state['page'] = 'analyze_genres'
    elif page_selection == "Chat with the Bot":
      st.session_state['page'] = 'chat_with_bot'
    else:
      st.session_state['page'] = 'main'
