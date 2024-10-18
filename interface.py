import streamlit as st
import base64
import functions as func
import json
from openai import OpenAI
import random

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


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


def set_username(userdata):
  st.session_state['user_data'] = userdata


def set_playlist(playlists):
  st.session_state['playlists'] = playlists


def page_selector():
  sidebar()
  if st.session_state['page'] == 'view_playlist':
    view_playlist()
  elif st.session_state['page'] == 'get_song_recommendations':
    get_song_recommendations()
  elif st.session_state['page'] == 'analyze_genres':
    analyze_genres()
  elif st.session_state['page'] == 'chat_with_bot':
    chat_with_bot()
  else:
    success_page()


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


def sidebar():
  css()
  # Display the user picture at the top of the sidebar
  userpicture = st.session_state['user_data']['images'][0]['url']
  st.sidebar.image(userpicture, width=100)
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
        ("Main page", "View Playlist", "Get Song Recommendations",
         "Analyze Genres", "Chat with the Bot"))

    # Set session state page based on selection
    if page_selection == 'View Playlist':
      st.session_state['page'] = 'view_playlist'
    elif page_selection == "Get Song Recommendations":
      st.session_state['page'] = 'get_song_recommendations'
    elif page_selection == "Analyze Genres":
      st.session_state['page'] = 'analyze_genres'
    elif page_selection == "Chat with the Bot":
      st.session_state['page'] = 'chat_with_bot'
    else:
      st.session_state['page'] = 'main'


def success_page():
  user_data = st.session_state['user_data']
  if user_data:
    st.markdown(
        f"<div class='title'>Welcome, {user_data['display_name']}!</div>",
        unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.write('You have successfully logged in to Spotify.')
    st.write(
        "Now you can explore your Spotify playlists and analyze your music!")

    get_ai_recommendations()

  else:
    st.error("User data not found. Please try logging in again.")


def get_ai_recommendations():
  user_data = st.session_state['playlists']
  if not user_data:
    st.error("User data not found. Please try logging in again.")
    return

  # Extract genres from user's playlists
  # user_genres = set()
  # for playlist in user_data['playlists']:
  #   for item in playlist['tracks']['items']:
  #     # Assuming each song has a 'genre' field. If not, you might need to fetch this separately
  #     genre = item['track'].get('genre', 'Unknown')
  #     user_genres.add(genre)

  # Define a list of all possible genres (this should be more comprehensive in a real application)
  all_genres = [
      "Rock", "Pop", "Hip Hop", "Jazz", "Classical", "Electronic", "Country",
      "R&B", "Blues", "Reggae", "Folk", "Metal", "Punk", "Soul", "Funk",
      "Disco", "Techno", "House", "Ambient", "Gospel"
  ]

  # Find genres the user hasn't listened to
  new_genres = [genre for genre in all_genres]

  if not new_genres:
    st.subheader(
        "You seem to have explored all genres! Here are some eclectic recommendations:"
    )
    st.divider()
    new_genres = random.sample(all_genres, 5)
  else:
    st.subheader(
        "Based on your listening history, here are some recommendations from genres you might not have explored:"
    )
    st.divider()

  # Use GPT to generate recommendations
  recommendations = []
  for genre in random.sample(new_genres, 5):
    prompt = f"Recommend a {genre} song that's not very well-known but is considered excellent by critics or genre enthusiasts. Include the artist name."
    response = client.chat.completions.create(model='gpt-4',
                                              messages=[{
                                                  'role': 'user',
                                                  'content': prompt
                                              }],
                                              max_tokens=50)
    recommendation = response.choices[0].message.content.strip()
    recommendations.append((genre, recommendation))

  # Display recommendations
  for genre, recommendation in recommendations:
    st.subheader(f"{genre}")
    st.write(recommendation)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

  st.caption(
      "***These recommendations are AI-generated and may not reflect actual songs. Always verify before listening!"
  )


def view_playlist():
  token = st.session_state['token_info']['access_token']

  st.markdown(f"<div class='title'>View your playlists !</div>",
              unsafe_allow_html=True)
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

  playlists_data = st.session_state['playlists']
  playlist_items = playlists_data['items']
  playlist_ids = [id['id'] for id in playlist_items]
  playlist_names = [playlist['name'] for playlist in playlist_items]
  songs = {}
  for playlist_name, playlist_id in zip(playlist_names, playlist_ids):
    playlist_tracks = func.get_user_playlists_items(token, playlist_id)
    playlist_songs = []
    for items in playlist_tracks:
      track = items['track']
      song_info = {
          'name': track['name'],
          'artist':
          track['artists'][0]['name'] if track['artists'] else 'Unknown',
          'album': track['album']['name'] if 'album' in track else 'Unknown',
          'image': track['album']['images'][0]['url']
      }
      playlist_songs.append(song_info)

    songs[playlist_name] = playlist_songs

  # Display total number of playlists
  st.subheader(f"You have {len(playlist_items)} playlists")

  # Create a selectbox for choosing a playlist
  selected_playlist_name = st.selectbox("Choose a playlist", playlist_names)

  # Find the selected playlist
  selected_playlist = next((playlist for playlist in playlist_items
                            if playlist['name'] == selected_playlist_name),
                           None)

  if selected_playlist:
    st.title(f"Playlist: {selected_playlist['name']}")

  col1, col2 = st.columns(2)

  # Show playlist cover directly
  with col1:
    st.image(selected_playlist['images'][0]['url'],
             width=200,
             caption="Playlist Cover")

  # Display additional playlist info
  with col2:
    st.write(f"Total tracks: {selected_playlist['tracks']['total']}")
    if 'description' in selected_playlist:
      st.write(f"Description: {selected_playlist['description']}")
    else:
      st.error("User data not found. Please try logging in again.")

  st.subheader("Songs in the Playlist:")
  container, container2 = st.columns([5, 1])
  song_list = songs[selected_playlist['name']]
  for song in song_list:
    photo, song_show = st.columns([1, 5])
    with container:
      with photo:
        st.image(song['image'], width=100)
      with song_show:
        st.write(f"*{song['name']}* \n\n\tby {song['artist']}")


def display_recommend(recommendations):
  for song in recommendations['song']:
    st.write(f"**{song['title']}** - Genre: {song['genre']}\n")


def get_song_recommendations():
  st.markdown(f"<div class='title'>Songs recommendation !</div>",
              unsafe_allow_html=True)
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
  desired_tempo = st.slider("Select desired BPM (Beats per Minute)", 50, 200,
                            100)
  desired_sentiment = st.selectbox(
      "Select desired Sentiment",
      ["Calm", "Dark", "Energetic", "Happy", "Romantic", "Sad"])
  desired_TS = (f"Tempo: {desired_tempo}, Sentiment: {desired_sentiment}")
  recommendations = json.loads(recommend_by_tempo_and_sentiment(desired_TS))
  display_recommend(recommendations)


def recommend_by_tempo_and_sentiment(desired_TS):
  system_prompt = """
  You are given a desired tempo and sentiment. Recommend at least 5 songs based on the given criteria.
  The output should be in JSON format, like this:
  {
  "song": [
  {
  "title": "Song Title 1", "genre": "Genre 1"
  },
  {
  "title": "Song Title 2", "genre": "Genre 2"
  },
  ...
  ]
  }
  """

  response = client.chat.completions.create(model='gpt-4o-mini',
                                            messages=[{
                                                'role': 'system',
                                                'content': system_prompt
                                            }, {
                                                'role': 'user',
                                                'content': desired_TS
                                            }],
                                            max_tokens=2000)

  return response.choices[0].message.content


def chat_with_bot():
  st.markdown(f"<div class='title'>Chat with Music Bot !</div>",
              unsafe_allow_html=True)
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

  st.markdown("<div class='chatbox-header'>Music Chatbot</div>",
              unsafe_allow_html=True)

  # Display chat messages from history on app rerun
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Chat input form
  with st.form(key='chat_form'):
    user_input = st.text_input("Type your message here:", key="chat_input")
    submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
      st.session_state.messages.append({"role": "user", "content": user_input})
      response = get_gpt_response(user_input)
      st.session_state.messages.append({
          "role": "assistant",
          "content": response
      })
      st.rerun()  # Rerun to refresh the chat display


def get_gpt_response(prompt):
  system_prompt = """
  You are a professional in music. Answer anything asked related to music and songs. Otherwise reply 'Sorry, I can't help you with that. Try asking something related to music.'
  """
  response = client.chat.completions.create(model='gpt-4',
                                            messages=[{
                                                'role': 'system',
                                                'content': system_prompt
                                            }, {
                                                'role': 'user',
                                                'content': prompt
                                            }],
                                            max_tokens=150)
  return response.choices[0].message.content


def analyze_genres():
  st.markdown(f"<div class='title'>Sort Genres !</div>",
              unsafe_allow_html=True)
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
  # Fetch user data (including playlists)
  user_data = st.session_state

  # If no playlists, display an error message
  if not user_data or not user_data['playlists']:
    st.error("No playlists found for this user.")
    return

  # Choose a playlist to sort songs from
  playlist_names = [playlist['name'] for playlist in user_data['playlists']]
  selected_playlist_name = st.selectbox("Choose a playlist to sort by genre",
                                        playlist_names)

  # Find the selected playlist
  selected_playlist = next((playlist for playlist in user_data['playlists']
                            if playlist['name'] == selected_playlist_name),
                           None)

  if selected_playlist:
    st.title(f"Playlist: {selected_playlist['name']}")

    # Initialize a dictionary to store songs by genre
    genre_dict = {}

    # Loop through the tracks in the playlist
    for item in selected_playlist['tracks']['items']:
      song = item['track']
      artist_name = song['artists'][0]['name']
      song_title = song['name']

      # Get the genre of the artist (mock data for now)
      genre = get_artist_genre(artist_name)

      # Add the song to the respective genre list
      if genre not in genre_dict:
        genre_dict[genre] = []
      genre_dict[genre].append(f"{song_title} by {artist_name}")

    # Display songs grouped by genre
    for genre, songs in sorted(genre_dict.items()):
      st.subheader(f"Genre: {genre}")
      for song in songs:
        st.write(f"- {song}")
