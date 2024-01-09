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


@dataclass(frozen=True)
class Message:
    """A Chat Message between between the user and assistant."""

    role: str
    text: str

    @property
    def id(self) -> str:
        """Identifier that uniquely identifies this message."""
        return str(hash(self))


def render(chat_log: list[Message]):
    # page title & favicon
    st.set_page_config(page_title="Olier", page_icon=OLIER_PNG)
    # inject css to style page
    st.markdown(f"<style>{STYLE_CSS}</style>", unsafe_allow_html=True)

    # page sidebar
    st.sidebar.image(LA_GRACE_LOGO)

    # main page
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

            if message.role == "assistant":
                columns = st.columns(12)
                columns[0].button(label=":thumbsup:", key=f"{message.id}_upvote", help="Upvote Olier's response")
                columns[1].button(label=":thumbsdown:", key=f"{message.id}_downvote", help="Downvote Olier's response")

    # copy chat log to clipboard
    columns = st.columns(12)
    columns[11].button(label=":clipboard:", help= "Copy chat to clipboard")

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
