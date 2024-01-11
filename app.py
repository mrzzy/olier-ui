#
# Olier
# Frontend
#

import json
from pathlib import Path
from typing import Generator, Optional, cast
import openai
import streamlit as st
import streamlit_antd_components as sac

from models import Message, State

# Settings
# assets
ASSETS_DIR = Path("assets")
OLIER_PNG = str(ASSETS_DIR / "Olier.png")
OLIER_SMALL_PNG = str(ASSETS_DIR / "olier-small.png")
LOTUS_PNG = str(ASSETS_DIR / "lotus.png")
LA_GRACE_LOGO = str(ASSETS_DIR / "la-grace-logo.png")
with open(ASSETS_DIR / "styles.css", "r") as f:
    STYLE_CSS = f.read()


# model
# response generation
MODEL_MAX_TOKENS = 1000
MODEL_TEMPERATURE = 0.4
# no. of message(s) passed as context
MODEL_CONTEXT_SIZE = 6

# dataset
DATA_DIR = Path("data")
# good samples: rated thumbs up by user
GOOD_DATA_DIR = DATA_DIR / "good"
# bad samples: rated thumbs down by user
BAD_DATA_DIR = DATA_DIR / "bad"
# no of message(s) saved in each data sample
DATA_SAMPLE_SIZE = 6
# create dataset directories if they do not exist
DATA_DIR.mkdir(exist_ok=True)
GOOD_DATA_DIR.mkdir(exist_ok=True)
BAD_DATA_DIR.mkdir(exist_ok=True)


def write_dataset(chat_log: list[Message], rating: bool):
    """Write chat log as a sample with the given rating label.

    Args:
        chat_log: List of messages to write as sample.
        rating: Rating True=Good, False=Bad label to give to the sample.
    """
    if len(chat_log) == 0:
        # nothing to do
        return
    # use timestamp of first message to construct filename
    filename = f"chat_log__{chat_log[0].timestamp.isoformat('_')}.json"
    sample_file = (GOOD_DATA_DIR if rating else BAD_DATA_DIR) / filename

    with sample_file.open("w") as f:
        json.dump([m.to_dict() for m in chat_log], f)


# OpenAI client
# configure openai client to access chatbot model
openai.api_base = "http://localhost:8000/v1"
# since we are accessing a local endpoint, no credentials are required
openai.api_key = "NA"


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
    button_idx = st.session_state[UI_UTILTY_BUTTONS]
    # only allow the user to rate once
    if s.rating is None:
        if button_idx == 0:
            # user rated thumbs up
            s.rating = True
        if button_idx == 1:
            # user rated thumbs down
            s.rating = False
        write_dataset(s.chat_log[-DATA_SAMPLE_SIZE:], rating=cast(bool, s.rating))
    if button_idx == 2:
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
        # user rating
        if s.rating == True:
            st.toast("Great. Olier will show you something similar next time.", icon="📝")
        elif s.rating == False:
            st.toast("Got it. Olier will show you something different next time.", icon="📝")

        # copy to clipboard
        if s.is_copying:
            # show code block with copy to clipboard function
            st.code("\n".join(str(m) for m in s.chat_log))
            # prompt user hover to access copy feature
            st.toast("Hover over the top right of the text box to copy.", icon="💡")

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
