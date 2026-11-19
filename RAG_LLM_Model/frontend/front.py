import streamlit as st
import os
from google import genai

client = genai.Client(
    api_key= os.getenv("GEMINI_API_KEY")
)

if "histry" not in st.session_state:
    st.session_state.histry = []
prompt = st.chat_input("prompt")

if prompt:
    st.session_state.histry.append(prompt)
    response = client.model.generate_content(
        model_name = "gemini-2.8-flash",
        contents = prompt
    )
    res = response.text
    st.session_state.histry.append(res)
for msg in st.session_state.histry:
    st.write(msg)


