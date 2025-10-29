import os
import yaml
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path


class Config:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config,cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance 

    def _load_config(self):
        
        '''     Singleton Config class
    - Đọc .env (API keys, secrets)
    - Đọc configs/settings.yaml (tham số ứng dụng)
    - Cung cấp cấu hình thống nhất cho toàn project
    '''
        # load  API from .env
        # load_dotenv()  Loai bo do chay tren streamlit cloud
        # Load YAML settings
        root_dir = Path(__file__).parent.parent.parent
        setting_path = os.path.join(root_dir, 'configs', 'setting.yaml')
        with open(setting_path,"r", encoding= "utf-8") as f:
            yaml_data = yaml.safe_load(f)
        
        # App infomation 
        app_cfg = yaml_data.get("app",{})
        self.APP_NAME = app_cfg.get("name", "Groq RAG Chatbot" )
        self.APP_VERSION = app_cfg.get("version", "1.0.0")
        
        # Model settings
        
        model_cfg = yaml_data.get("model", {})
        self.LLM_PROVIDER = model_cfg.get("llm_provider", "groq")
        self.LLM_MODEL = model_cfg.get("llm_name", "llama3-8b-8192")
        self.MAX_TOKENS = model_cfg.get("max_tokens", 512)
        self.TEMPERATURE = model_cfg.get("temperature", 0.7)
        self.EMBEDDING_MODEL = model_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        
        # API-- keys
        # Spliiter for RAG 
        model_rag = yaml_data.get("rag",{})
        self.CHUNK_SIZE = model_rag.get('chunk_size')
        self.CHUNK_OVERLAP = model_rag.get('chunk_overlap')
        
        #self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.GROQ_API_KEY = self._get_secret("GROQ_API_KEY")
        
        # Other environments
        retrival_config = yaml_data.get("retrieval",{})
        self.TYPE_RETRIEVAL =retrival_config.get("type[0]","hybrid")
        self.K_FINAL =  retrival_config.get("k_final")
        self.K_VECTOR =retrival_config.get("k_vector")
        self.K_BM25 = retrival_config.get("k_bm25")
        ## Rerank Model
        reranker_cfg = yaml_data.get("reranker",{})
        self.RERANKER_MODEL = reranker_cfg.get("model", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.ENABLE = reranker_cfg.get('enabled')
    
    
        
        
    def _get_secret(self, key: str):
        try:
        # 1. Kiểm tra trong Streamlit secrets
            if hasattr(st, 'secrets'):
                if key in st.secrets:
                    value = st.secrets[key]
                    if value:
                        print(f"INFO: Đã lấy thành công {key} từ Streamlit secrets")
                        return value

            print(f"WARNING: Không tìm thấy {key} trong Streamlit secrets.")
            return None

        except Exception as e:
            print(f"ERROR: Lỗi khi truy cập {key}: {str(e)}")
            return None

    def summary(self):
        '''  in nhanh cau hinh hien tai'''
        return {
            "app": self.APP_NAME,
            "model": self.LLM_MODEL,
            "embedding": self.EMBEDDING_MODEL,
            "type_retriaval" : self.TYPE_RETRIEVAL
            #"data_path": self.VECTOR_STORE_PATH,
            # "env": self.ENVIRONMENT,          
        }

config =Config()
config._load_config()
print(config.summary())
print(config.GROQ_API_KEY)