import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="PSD",
    layout="wide",
    initial_sidebar_state="collapsed",
)

components.iframe(
    "https://riskanana06.github.io/PSD/",
    height=1000,
    scrolling=True,
)