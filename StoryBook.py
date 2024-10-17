import os

import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def story_gen(prompt):
    system_prompt = """
  You are a world popular writer for young adults fiction short stories.
  Given a concept, generate a short story relevent to the thems of the concept and having a twist end.
  """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=1,
        max_tokens=2000,
        frequency_penalty=1,
    )
    return response.choices[0].message.content


def art_gen(prompt):
    response = client.images.generate(model="dall-e-2",
                                      prompt=prompt,
                                      quality="standard",
                                      n=1,
                                      size="1024x1024")
    return response.data[0].url


def design_def(prompt):
    system_prompt = """
    You will be given a short story. Generate a prompt for a cover art that is suitable for the story. The prompt is for dall-e-2
  """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
    )
    return response.choices[0].message.content


prompt = st.text_input("Enter a prompt")
if (st.button("Generate")):
    story = story_gen(prompt)
    design = design_def(story)
    art = art_gen(design)

    st.write(story)
    st.divider()
    st.caption(design)
    st.divider()
    st.image(art)
