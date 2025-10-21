import streamlit as st
from  app.handler.chat_handler import ChatHandler

st.title("💬 Smart Chatbot with RAG")

if "chat_handler" not in st.session_state:
    st.session_state.chat_handler = ChatHandler(use_id="demo")

chat_handler = st.session_state.chat_handler

uploaded_file = st.file_uploader("Upload a document (CSV/PDF)...", type=["csv", "pdf"])
if uploaded_file:
    with open(f"data/uploads/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    chat_handler.file_process(f"data/uploads/{uploaded_file.name}")
    st.success("✅ File loaded successfully!")

query = st.text_input("Ask me something about your document:")
placeholder = st.empty()

if st.button("Send"):
    for token in chat_handler.stream_chat(query, placeholder):
        pass

if st.button("🧹 Clear chat"):
    chat_handler.clear_history()
    st.experimental_rerun()

if st.button("🗑️ Delete session"):
    chat_handler.delete_session()
    st.success("Session deleted.")
    st.stop()
