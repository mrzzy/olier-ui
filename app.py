#
# Olier
# Frontend
#

from os import path
from typing import Generator, Optional, cast
import openai
import streamlit as st
import streamlit_antd_components as sac

from models import Message, State

# Settings
# assets
ASSETS_DIR = "assets"
OLIER_PNG = path.join(ASSETS_DIR, "Olier.png")
OLIER_SMALL_PNG = path.join(ASSETS_DIR, "olier-small.png")
LOTUS_PNG = path.join(ASSETS_DIR, "lotus.png")
LA_GRACE_LOGO = path.join(ASSETS_DIR, "la-grace-logo.png")
# openai client
OPENAI_API_BASE = "http://localhost:8000/v1"
OPENAI_API_KEY = "NA"
# model
# response generation
MODEL_MAX_TOKENS = 1000
MODEL_TEMPERATURE = 0.4
# no. of message passed as context
MODEL_CONTEXT_SIZE = 6


with open(path.join(ASSETS_DIR, "styles.css"), "r") as f:
    STYLE_CSS = f.read()


# OpenAI client
# configure openai client to access chatbot model
openai.api_base = OPENAI_API_BASE
# since we are accessing a local endpoint, no credentials are required
openai.api_key = OPENAI_API_KEY


@st.cache_data
def model_id() -> str:
    """Caches & returns the first model offered by the OpenAI API"""
    models = openai.Model.list()
    return cast(dict, models)["data"][0]["id"]


@st.cache_resource(max_entries=1)
def get_response_stream(message_idx: int) -> Generator[dict, None, None]:
    """Stream the chatbot model's response to the user's request at message index.

    Args:
        message_idx: Message index of the user's request in the chat log.

    Returns:
        Generator that streams the response from the model.
    """
    # limit context to 3 user-assistant exchanges
    context = st.session_state["state"].chat_log[
        message_idx - MODEL_CONTEXT_SIZE : message_idx + 1
    ]

    return cast(
        Generator[dict, None, None],
        openai.ChatCompletion.create(
            model=model_id(),
            messages=[m.to_openai() for m in context],
            max_tokens=MODEL_MAX_TOKENS,
            temperature=MODEL_TEMPERATURE,
            # generate only 1 response choice
            n=1,
            stream=True,
        ),
    )


# UI Frontend
# ui element keys
UI_CHAT_INPUT = "chat_input"
UI_UTILTY_BUTTONS = "utility_buttons"


def draw_message(message: Message):
    """Draw the given message in the UI"""
    with st.chat_message(
        name=message.role,
        avatar=OLIER_SMALL_PNG if message.role == "assistant" else LOTUS_PNG,
    ):
        st.write(message.content)


def on_submit_chat_input(s: State):
    # add user's message
    s.chat_log.append(Message(role="user", content=st.session_state[UI_CHAT_INPUT]))
    # mark user's last mssage as currently streaming
    s.streaming_idx = len(s.chat_log) - 1
    # add empty message to store chatbot's response
    s.chat_log.append(Message(role="assistant", content=""))


def on_click_utility_button(s: State):
    if st.session_state[UI_UTILTY_BUTTONS] == 2:
        # toggle clipboard
        s.is_copying = not s.is_copying


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
    if s.streaming_idx is not None:
        # currently streaming response from chatbot
        # retrieve response delta from chatbot via openai client
        try:
            chunk = next(get_response_stream(s.streaming_idx))
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                s.chat_log[-1] = s.chat_log[-1].append(content)
        except StopIteration:
            # finished response: stop streaming
            s.streaming_idx = None
    # draw chat messages
    for message in s.chat_log:
        draw_message(message)

    # only render utility buttons if not currently streaming
    if s.streaming_idx is None:
        sac.buttons(
            [
                # chat rating button
                sac.ButtonsItem(icon="hand-thumbs-up"),
                sac.ButtonsItem(icon="hand-thumbs-down"),
                # copy chat log to clipboard button
                sac.ButtonsItem(icon="copy"),
            ],
            index=None,
            return_index=True,
            key=UI_UTILTY_BUTTONS,
            on_change=on_click_utility_button,
            args=(s,),
        )

        # copy to clipboard
        if s.is_copying:
            # show code block with copy to clipboard function
            st.code("\n".join(str(m) for m in s.chat_log))
            # prompt user hover to access copy feature
            st.toast("Hover over the top right of the text box to copy.")

    # chatbot input
    st.chat_input(
        "Ask Olier about...",
        key=UI_CHAT_INPUT,
        on_submit=on_submit_chat_input,
        args=(s,),
    )

    return s


# init render state if it does not exist
if "state" not in st.session_state:
    st.session_state["state"] = State(chat_log=[])

st.session_state["state"] = render(st.session_state["state"])
# schedule a rerender if we are still streaming response
if st.session_state["state"].streaming_idx is not None:
    st.rerun()
