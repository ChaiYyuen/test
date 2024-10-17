import streamlit as st
from imageloader import render_image


def login_page(auth_url):
  st.markdown(
      "<div class='title'>GenreSync: Tune in to Musical Diversity</div>",
      unsafe_allow_html=True)
  st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
  logo = "/pic/Spotify.png"
  render_image("/pic/Spotify.png")
  left_co, cent_co, last_co = st.columns(3)
  with cent_co:
    st.image(logo)
  st.markdown('<p class="subtitle">Log in to your Spotify account!</p>',
              unsafe_allow_html=True)

  # Spotify Login Button (Mock login functionality)
  if st.link_button('Log in with Spotify', auth_url):
    st.success("Logging...")
    st.session_state['logged_in'] = True
    st.session_state['page'] = 'main'  # Default page after login
    st.rerun()  # Rerun the app after login
