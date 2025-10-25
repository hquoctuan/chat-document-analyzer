import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.handler.chat_handler import ChatHandler
from datetime import datetime

st.set_page_config(
    page_title="💬 Smart RAG Chatbot",
    page_icon="🤖",
    layout="wide",
)

# ==== SIDEBAR ====
with st.sidebar:
    st.header("⚙️ Controls")
    if "chat_handler" not in st.session_state:
        st.session_state.chat_handler = ChatHandler(user_id="demo")

    chat_handler = st.session_state.chat_handler

    # Upload file
    uploaded_file = st.file_uploader("📎 Upload CSV/PDF", type=["csv", "pdf"])
    if uploaded_file:
        file_path = f"data/uploads/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
       
        chat_handler.file_process(file_path)
        st.success("✅ File processed successfully!")

    # Session tools
    st.divider()
    if st.button("🆕 New Chat"):
        st.session_state.messages = []
        st.rerun(),

    if st.button("🧹 Clear Memory"):
        chat_handler.clear_history()
        st.session_state.messages = []
        st.rerun(),

    if st.button("🗑️ Delete Session"):
        chat_handler.delete_session()
        st.session_state.messages = []
        st.success("Session deleted.")
        st.stop()

# ==== MAIN CHAT AREA ====
st.title("💬 Analyzer Document with LLM")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container (scrollable)
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

# ==== INPUT AREA (fixed at bottom) ====
user_query = st.chat_input("Type your message here...")

if user_query:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message immediately
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    # Placeholder for assistant response
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        response_text = ""
        thinking_msg = "🤔 *I'm Thinking...*"
        placeholder.markdown(thinking_msg)
        # Stream chat from handler
        for chunk in chat_handler.stream_chat(user_query, placeholder):
            response_text += chunk
            placeholder.markdown(response_text)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response_text})
