import streamlit as st
import base64


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
  if (st.button('Log in with Spotify', auth_url)):
    st.success("Logging...")
    st.session_state['logged_in'] = True
    st.session_state['page'] = 'main'  # Default page after login
    st.rerun()  # Rerun the app after login
