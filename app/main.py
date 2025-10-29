import sys
import streamlit as st
import time
import os

# Path run
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.handler.chat_session_handler import ChatSessionHandler


#Congifg

st.set_page_config(page_title="Document Analyzer Chatbot", page_icon="🤖", layout="wide")
# CSS load
css_path = os.path.join(os.path.dirname(__file__), "static", "style.css")

if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("⚠️ CSS file not found: static/style.css")

USER_ID = "demo"
BASE_DIR = "data/sessions"

# ==========================================
# Intinilize session state
# ==========================================
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = ChatSessionHandler.list_user_sessions(USER_ID)

# ChatSessionHandler mặc định để tránh tạo session thừa
if "chat_obj" not in st.session_state:
    st.session_state.chat_obj = None  # chỉ tạo khi user upload hoặc nhập prompt

# ==========================================
# 🧩 Sidebar – Danh sách chat
# ==========================================
with st.sidebar:
    st.title("💬 Chat Sessions")

    if st.button("New Chat", use_container_width=True):
        # Chỉ reset context, KHÔNG tạo session mới ngay lập tức
        st.session_state.chat_obj = None
        # Cập nhật danh sách sessions (không thêm session mới)
        st.session_state.chat_sessions = ChatSessionHandler.list_user_sessions(USER_ID)
        st.rerun()

    st.markdown("---")
    sessions = st.session_state.chat_sessions

    if not sessions:
        st.info("No chat session.")
    else:
        for s in sessions:
            session_id = s.get("session_id")
            title = s.get("title", "Untitled")

            col1, col2 = st.columns([0.8, 0.2])
            if col1.button(title, key=f"open_{session_id}", use_container_width=True):
                # Load lại session cũ
                chat = ChatSessionHandler(user_id=USER_ID, session_id=session_id)
                chat.load_chat_history()

                # Khôi phục lại engine từ vector_store cũ
                restored = chat.load_engine_from_disk()
                if not restored:
                    st.warning(" Không thể khôi phục engine, cần upload lại file.")
                st.session_state.chat_obj = chat
                st.rerun()

            if col2.button("🗑️", key=f"delete_{session_id}", help="Delete this chat session"):
                # Xóa session được chọn
                ChatSessionHandler(user_id=USER_ID, session_id=session_id).detete_session()

                # Nếu session hiện tại bị xóa → loại bỏ nó, KHÔNG tạo new chat tự động
                if (
                    "chat_obj" in st.session_state
                    and st.session_state.chat_obj
                    and st.session_state.chat_obj.session_id == session_id
                ):
                    del st.session_state.chat_obj  
                # Cập nhật danh sách sessions hiển thị
                st.session_state.chat_sessions = ChatSessionHandler.list_user_sessions(USER_ID)
                st.rerun()

# ==========================================
# Main UI
# ==========================================
chat_obj: ChatSessionHandler = st.session_state.chat_obj

# Nếu chưa có chat_obj (chưa tạo session), hiển thị tiêu đề mặc định
if chat_obj is not None:
    meta = chat_obj.get_metadata()
else:
    meta = {"title": "New Chat", "file_uploaded": False}

st.markdown("<h2 style='text-align:center;'> Chat Document Analyzer </h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'> In chat session: <b>{meta.get('title', 'New Chat')}</b></p>", unsafe_allow_html=True)
st.markdown("---")


# 📎 Upload file (chỉ khi chưa có)

if not meta.get("file_uploaded", False):
    uploaded_file = st.file_uploader("📂 Upload file to chat", type=["pdf", "csv"])
    if uploaded_file:
        # 🔸 Chỉ khi user upload mới tạo session
        if chat_obj is None:
            st.session_state.chat_obj = ChatSessionHandler(user_id=USER_ID)
            chat_obj = st.session_state.chat_obj

        temp_dir = os.path.join(BASE_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("⚙️ Process data..."):
            success = chat_obj.file_process(temp_path)

        os.remove(temp_path)
        if success:
            st.success("✅ Successful procesing data!")
            # Sau khi xử lý xong, cập nhật meta và danh sách sessions
            st.session_state.chat_sessions = ChatSessionHandler.list_user_sessions(USER_ID)
            st.rerun()
        else:
            st.error("❌Fail, please try again.")


#Streaming

# Hiển thị lại lịch sử chat nếu đã có session
if chat_obj is not None:
    for msg in chat_obj.memory.chat_memory.messages:
        with st.chat_message(msg.type):
            st.markdown(msg.content)

prompt = st.chat_input(" Enter your message...")

if prompt:
    # 🔸 Chỉ khi user nhập prompt mới tạo session (nếu chưa có)
    if chat_obj is None:
        st.session_state.chat_obj = ChatSessionHandler(user_id=USER_ID)
        chat_obj = st.session_state.chat_obj
        meta = chat_obj.get_metadata()

    if not meta.get("file_uploaded", False):
        st.warning("⚠️ Please upload document.")
        st.stop()

    is_first = not chat_obj.memory.chat_memory.messages

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        st.write_stream(chat_obj.stream_chat(prompt, placeholder))

    if is_first:
        chat_obj.summarize_title(prompt)
        st.session_state.chat_sessions = ChatSessionHandler.list_user_sessions(USER_ID)
        st.rerun()
    else:
        st.rerun()
