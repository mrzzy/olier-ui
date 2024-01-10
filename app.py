#
# Olier
# Frontend
#

from dataclasses import dataclass
from os import path
from typing import Optional, cast
import streamlit as st
import streamlit_antd_components as sac

ASSETS_DIR = "assets"
OLIER_PNG = path.join(ASSETS_DIR, "Olier.png")
OLIER_SMALL_PNG = path.join(ASSETS_DIR, "olier-small.png")
LOTUS_PNG = path.join(ASSETS_DIR, "lotus.png")
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


@dataclass
class State:
    """ "
    Encapsulates the rendering state of the Olier Frontend UI.

    Attributes:
        chat_log: Chat log of messages between the user & chatbot to render.
        button_idx: Optional. Index of the utility buttons (copy, thumbs-up,
            thumbs-down) that is selected by the user or None if none are selected.
    """

    chat_log: list[Message]
    button_idx: Optional[int] = None


def render(s: State) -> State:
    """
    Render the Olier Frontend UI.
    Args:
        s: Render UI to match given state.
    Returns:
        Rendering state with any changes made by the user.
    """
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
    for message in s.chat_log:
        with st.chat_message(
            name=message.role,
            avatar=OLIER_SMALL_PNG if message.role == "assistant" else LOTUS_PNG,
        ):
            st.write(message.text)

    s.button_idx = cast(
        Optional[int],
        sac.buttons(
            [
                # chat rating button
                sac.ButtonsItem(icon="hand-thumbs-up"),
                sac.ButtonsItem(icon="hand-thumbs-down"),
                # copy chat log to clipboard button
                sac.ButtonsItem(icon="copy"),
            ],
            index=s.button_idx,
            return_index=True,
        ),
    )

    # chatbot input
    st.chat_input("Ask Olier about...")

    return s


# init render state if it does not exist
if "state" not in st.session_state:
    st.session_state["state"] = State(
        chat_log=[
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


st.session_state["state"] = render(st.session_state["state"])
