import os, sys, time
import streamlit as st

# Cấu hình đường dẫn dự án
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.handler.chat_session_manager import ChatSessionManager

# ==============================
# ⚙️ 1. Cấu hình ban đầu
# ==============================
st.set_page_config(
    page_title="📚 Chat Document Analyzer",
    layout="wide",
    page_icon="💬"
)

# ==============================
# 🧭 2. Khởi tạo ChatSessionManager
# ==============================
USER_ID = "demo_user"
manager = ChatSessionManager(user_id=USER_ID)

# ==============================
# 🎨 3. Sidebar: Quản lý các đoạn chat
# ==============================
st.sidebar.title("💬 Chat Sessions")

# Nút tạo đoạn chat mới
if st.sidebar.button("➕ New Chat", use_container_width=True):
    session_id = manager.create_session()
    st.session_state["current_session"] = session_id
    st.rerun()

# Lấy danh sách các session
sessions = manager.list_sessions()

# Nếu có session
if sessions:
    options =  [s['title'] for s in sessions]
    selected = st.sidebar.radio("Select a conversation:", options)
    idx = options.index(selected)
    session_id = sessions[idx].get("id") or sessions[idx].get("session_id")
else:
    session_id = st.session_state.get("current_session")

# ==============================
# 📂 4. Load hoặc tạo mới session
# ==============================
if not session_id:
    st.markdown(
        """
        <div style='text-align: center; padding-top: 100px;'>
            <h1>🤖 <b>Chat Document Analyzer</b></h1>
            <p>Start a new chat or select one from the sidebar</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# Nạp ChatHandler cho session hiện tại
handler = manager.load_session(session_id)

# ==============================
# 📎 5. Upload tài liệu vào session
# ==============================
st.sidebar.markdown("---")
st.sidebar.subheader("📎 Add Document")

uploaded_file = st.sidebar.file_uploader("Upload CSV or PDF", type=["csv", "pdf"])
if uploaded_file:
    file_path = os.path.join(handler.session_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"✅ Uploaded: {uploaded_file.name}")

    with st.spinner("Building Vector Database..."):
        handler.file_process(file_path)
        st.sidebar.success("🧠 Vector Store ready!")

# ==============================
# 💬 6. Giao diện chính Chatbot
# ==============================
st.markdown(
    """
    <div style='text-align:center; padding: 10px 0;'>
        <h2>🤖 <b>DocuMind Assistant</b></h2>
        <p style='color: gray;'>Your intelligent assistant for document-based Q&A</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Hiển thị lịch sử chat
if handler.memory.chat_memory.messages:
    for msg in handler.memory.chat_memory.messages:
        if msg.type == "human":
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant").write(msg.content)
else:
    st.info("No chat yet — upload a document and start asking questions!")

# ==============================
# 🧠 7. Chat input
# ==============================
query = st.chat_input("Ask something about your document...")

if query:
    st.chat_message("user").write(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = handler.ask(query)
            st.write(answer)

    # Nếu là câu hỏi đầu tiên → sinh tiêu đề
    if len(handler.memory.chat_memory.messages) <= 2:
        manager.summarize_title(session_id, query)

# ==============================
# 🗑️ 8. Delete chat
# ==============================
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Delete this chat", use_container_width=True):
    manager.delete_session(session_id)
    st.success("Chat deleted successfully.")
    st.rerun()
