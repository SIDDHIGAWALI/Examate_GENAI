import streamlit as st
from google import genai
import requests
import json
# client = genai.Client(
#     api_key="apikey"
# )

if "histry" not in st.session_state:
    st.session_state.histry = []

prompt = st.chat_input("prompt")

baseUrl = "http://127.0.0.1:8000/"

if prompt:
    st.session_state.histry.append(prompt)

    response = requests.get(f"{baseUrl}/{prompt}")
    res = response.json()
    st.session_state.histry.append(res)

for msg in st.session_state.histry:
    st.write(msg)