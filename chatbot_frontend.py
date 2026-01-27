import streamlit as st
from chatbot_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ******************************** utility functions **************************************
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def load_conversation_by_thread_id(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


# ******************************* session setup *******************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])


# ******************************** Sidebar UI *******************************************
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat", key="new_chat_btn"):
    reset_chat()

st.sidebar.divider()
st.sidebar.subheader("💬 My Conversations")

for thread_id in st.session_state['chat_threads']:

    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get("messages", [])

    if messages:
        heading = messages[0].content[:30]
    else:
        heading = "New Conversation"

    # ✅ UNIQUE KEY FIX
    if st.sidebar.button(
        heading,
        key=f"thread_btn_{thread_id}"
    ):
        st.session_state['thread_id'] = thread_id

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({
                "role": role,
                "content": msg.content
            })

        st.session_state['message_history'] = temp_messages


# ******************************** Chat UI *******************************************
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input("Type your message...")

if user_input:
    # show user message
    st.session_state['message_history'].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {
            "thread_id": st.session_state['thread_id']
        }
    }

    with st.chat_message("assistant"):

        def ai_stream():
            for chunk, _ in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(chunk, AIMessage):
                    yield chunk.content

        ai_response = st.write_stream(ai_stream)

    st.session_state['message_history'].append({
        "role": "assistant",
        "content": ai_response
    })
