import streamlit as st

#set the app title
st.title("My first streamlit app")

#shell
#streamlit run filename

st.write("Welcome to my first app")
st.button("Reset", type="primary")
if (st.button("Say Hello")):
  st.write("Hi, hello there")
else:
  st.write("Goodbye")

