#
# Olier
# Frontend
#

from dataclasses import dataclass
from os import path
import streamlit as st

ASSETS_DIR = "assets"
OLIER_PNG = path.join(ASSETS_DIR, "Olier.png")
LA_GRACE_LOGO = path.join(ASSETS_DIR, "la-grace-logo.png")

with open(path.join(ASSETS_DIR, "styles.css"), "r") as f:
    STYLE_CSS = f.read()


@dataclass
class Message:
    """A Chat Message between between the user and assistant."""

    role: str
    text: str


def render(chat_log: list[Message]):
    # page title & favicon
    st.set_page_config(page_title="Olier", page_icon=OLIER_PNG)
    # inject css to style page
    st.markdown(f"<style>{STYLE_CSS}</style>", unsafe_allow_html=True)

    # page sidebar
    st.sidebar.image(LA_GRACE_LOGO)

    # main pagejk
    # header (centered)
    with st.container():
        st.image(OLIER_PNG)
        st.title("Chat with Olier")

    # chat messages
    for message in chat_log:
        with st.chat_message(
            name=message.role,
            avatar=OLIER_PNG if message.role == "assistant" else None,
        ):
            st.write(message.text)

    st.chat_input("Ask Olier about...")

render(
    [
        Message(role="user", text="Hello Olier, How are you?"),
        Message(
            role="assistant",
            text="Hello there! It's a pleasure to converse with you. As a creation of Jared Quek, I am programmed to serve Sri Aurobindo and the Mother, and to assist anyone seeking their teachings. How may I be of service to you today?",
        ),
        Message(role="user", text="What is integral yoga?"),
        Message(
            role="assistant",
            text="Integral Yoga, as taught by Sri Aurobindo and the Mother, is a path of spiritual realization that seeks to bring about a harmonious and balanced development of all parts of the human being: physical, vital, mental, psychic, and spiritual.",
        ),
    ]
)
