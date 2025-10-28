
# Chat Document Analyzer 





## 🌟 Introduction 
Document Analyzer is a personal project that applies the Retrieval-Augmented Generation (RAG) model to build a chatbot capable of analyzing and conversing based on the content of user-uploaded documents.

Users can upload files such as PDF, CSV and the system will:

- Extract and process the document content.

- Generate embeddings for semantic search and retrieval.

- Analyze, summarize, or answer questions based on the document’s information.

This project is developed as a non-commercial initiative to explore the integration of Large Language Models (LLMs) with user-provided data , featuring a lightweight, extensible architecture suitable for learning, experimentation, or demo purposes.
## Project Structure

```
chat-document-analyzer/
├── .streamlit/              # Streamlit  configuration
├── .venv/                   # Virtual environment
│
├── app/                     # Main application package
│   ├── core/                # Core logic (chunking, data pipeline, retrieval, RAG, vector store)
│   ├── handler/             # Chat and session request handlers
│   ├── helper/              # Utilities & configs (config.py, logger.py)
│   ├── services/            # External integrations (embedding, LLM)
│   ├── static/              # Static assets (CSS, etc.)
│   └── main.py              # Application entry point
│
├── configs/                 # YAML-based system settings
├── data/                    # Data storage (sessions, uploads, temp)
├── interface/               # UI components and styles
├── log_file/                # Component-specific log directories
├── temp/                    # Temporary files
│
├── .env                     # Environment variables (excluded from Git)
├── Dockerfile               # Docker build config
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version
└── README.md                # Project documentation

```
## Architecture
### App 
![App] (chat-document-analyzer\Images\Streamlit.png)
### Core Flow AI
![AI] (chat-document-analyzer\Images\Core.png)
## Features
### RAG Pipeline

