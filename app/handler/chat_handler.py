import os
import time
import hashlib
import shutil
from typing import Any, List, Optional, Generator
# Langchain lib
from langchain.memory import ConversationBufferMemory
from app.helper.logger import get_logger
from app.services.embedding_service import EmbeddingService
from app.services.llama_service import GroqLlamaService
from app.core.data_loader import DataLoader
from app.core.chunk_handler import ChunkHandler
from app.core.rag_engine import RagEngine
from app.core.vector_store import VectorStore
from app.core.rag_engine import RagEngine
from app.core.retriaval_handler import RetrivalHandler
from app.core.data_pipeline import DataPipeLine
from app.config import config

logger = get_logger('ChatHandler')

def compute_hash_lib(file_path: str) -> str:
    """Tạo hash md5 cho file để tái sử dụng vector DB"""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class ChatHandler():
    def __init__(self, use_id:str='guest',base_dir:str="data"):
        self.user_id = use_id
        self.session_id = str(int(time.time()))
        self.base_dir =base_dir
        self.session_dir = os.path.join(base_dir,f"session_{use_id}_{self.session_id}")
        os.makedirs(self.session_dir,exist_ok=True)
        
        self.TOP_k = config.K_FINAL
        
        # Service
        self.llm = GroqLlamaService()
        self.ebedding_service = EmbeddingService()
        self.ebedding_model = EmbeddingService().model
        self.vector_store  = VectorStore()
        self.retriver_handler = RetrivalHandler()
        self.pipe_line = DataPipeLine()
        
        #Memory ,
        self.memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True)
        
        #Status
        self.current_file = None
        self.current_file_path =None
        self.retriver = None
        self.engine = None
        logger.info(f" Chat Handler intialized for user {self.user_id}")
        
    # Load, build pipe line
    def file_process(self,file_path:str)-> bool:
        try:
            if not os.path.exists(file_path):
                logger.error('File not found ',(file_path))
                return False
            self.current_file_path = file_path
            self.current_file_hash = compute_hash_lib(file_path)
            # Folder vector store with session + hash_file
            vector_dir = os.path.join(self.session_dir,self.current_file_hash,"vector_store")
            os.makedirs(vector_dir,exist_ok= True)
            logger.info(f" Start runing data pipe line process for file {file_path}")
            index_path,chunks = self.pipe_line.process(file_path=file_path,save_dir=vector_dir)
            ## Load FAISS  index
            vt_store = self.vector_store.load_vectore_store(
                save_dir=vector_dir,
                embedding_model= self.ebedding_model
                
            )
            #Build retriver, engine
            self.retriver = self.retriver_handler.build(vector_store= vt_store,all_docs= chunks)
            self.engine = RagEngine(retriver= self.retriver)
            logger.info(f" Chat Handler Ready for Retriver ")
        except Exception as e:
            logger.error(f"Chat Handler process Fail {e}")
            return False
        
    def ask(self,question : str)-> str:
        ''' Input : question throught engine  -> answer'''
        if not self.engine:
            return 'No document upload. Please upload knowledge for chatting'
        try:
            self.memory.chat_memory.add_user_message(question)
            logger.info(f' Query received')
            answer = self.engine.gernerate(question)
            self.memory.chat_memory.add_ai_message(answer)
            return answer
        except Exception as e:
            logger.error(f'Error generating for quesion')
            return 'Sorry, something  went wrong during answering'
        
    def stream_chat(self,question: str, placeholder: Any)-> Generator[str, None,None]:
        '''Streaming chat '''
        if not self.engine:
            yield 'Please uploade docmument first'
            return
        try:
            self.memory.chat_memory.add_ai_message('I am assitant chat document, please uplaod document first')
            self.memory.chat_memory.add_user_message(question)
            placeholder.markdown("🤔 *Thinking...*")
            docs = self.retriver_handler.get_relevant_documents(question)
            context ="\n\n".join([d.page_content for d in docs[:self.TOP_k]])
            prompt = self.engine.format_prompt(context=context,question=question)
            response = ""
            for chunk in self.engine.llm.stream(prompt):
                text = getattr(chunk, "content", "")
                response += text
                placeholder.markdown(response)
                yield text
             # Save memory
            self.memory.chat_memory.add_ai_message(response)
            yield "\n.  "
        except Exception as e: 
            logger.error(f' Erro streaming chat{e}')
            yield "\n. "
                
    def clear_history(self):
        self.memory.clear()
        logger.info('Clear chat memory')

def delete_session(self):
        """Xóa toàn bộ dữ liệu session (file upload, vector DB, memory)."""
        try:
            if self.current_file_path and os.path.exists(self.current_file_path):
                os.remove(self.current_file_path)

            if self.current_file_hash:
                hash_dir = os.path.join(self.session_dir, self.current_file_hash)
                shutil.rmtree(hash_dir, ignore_errors=True)

            if os.path.exists(self.session_dir) and not os.listdir(self.session_dir):
                shutil.rmtree(self.session_dir, ignore_errors=True)

            self.clear_history()
            self.engine = None
            self.retriever = None
            self.current_file_hash = None
            self.current_file_path = None

            logger.info("🗑️ Session deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting session: {e}")
            return False
    
        

    
        

        
        
    
