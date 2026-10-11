import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="PSD",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            max-width: 100%;
        }

        [data-testid="stAppViewContainer"] {
            overflow: hidden;
        }

        iframe {
            display: block;
            width: 100%;
            border: none;
            height: calc(100vh - 70px);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

components.iframe(
    "https://riskanana06.github.io/PSD/",
    height=1000,
    scrolling=True,
)