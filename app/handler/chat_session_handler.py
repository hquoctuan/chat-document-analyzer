import os 
import json 
import time
import shutil

from typing import Dict,Optional,Any, Generator,List
from langchain.memory import ConversationBufferMemory
from app.helper.logger import get_logger
from app.services.embedding_service import EmbeddingService
from app.services.llama_service import GroqLlamaService
from app.core.data_pipeline import DataPipeLine
from app.core.chunk_handler import ChunkHandler
from app.core.data_loader import DataLoader
from app.core.vector_store import VectorStore
from app.core.retriaval_handler import RetrivalHandler
from app.core.rag_engine import RagEngine
from app.config import config

logger = get_logger("ChatSession")

class ChatSessionHandler:
    '''
    Quan ly va van hanh toan bo chat
    '''
    def __init__(self,user_id:str,session_id:Optional[str]= None, base_dir:str ="data/sessions"):
        self.user_id = user_id
        self.session_id = session_id or str(time.time())
        # thu muc nguoi dung + sesssion
        self.user_dir = os.path.join(base_dir, f"user_{user_id}")
        self.session_dir = os.path.join(self.user_dir, f"session_{self.session_id}") 
        self.upload_dir = os.path.join(self.session_dir, "uploads")                 
        self.vector_dir = os.path.join(self.session_dir, "vector_store")   
        os.makedirs(self.session_dir, exist_ok= True )
        os.makedirs(self.upload_dir,exist_ok= True)
        os.makedirs(self.vector_dir,exist_ok=True)
        
        # Metadata
        self.meta_path = os.path.join(self.session_dir,"metadata.json")
        if not os.path.exists(self.meta_path):
            self._create_metadata() 
        
        #Service
        self.llm = GroqLlamaService()
        self.embedding_service = EmbeddingService().model
        self.vectore_store = VectorStore()
        self.retriever_handler  = RetrivalHandler()
        self.pipe_line = DataPipeLine()
        self.memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)
        
        #State
        self.engine = None
        self.retriever = None
        self.current_path = None
        logger.info(f" Intialize Chat SEssion for uer {user_id}, session {session_id}")
        
    def _create_metadata(self):
        meta = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": "New Chat",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_uploaded": False                           
        }
        with open(self.meta_path,"w",encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            
    def update_metadata(self,**kwargs):
        if not os.path.exists(self.meta_path):
            self._create_metadata()
        with open(self.meta_path,"r+",encoding="utf-8") as f:
            meta = json.load(f)
            meta.update(kwargs)
            f.seek(0)
            json.dump(meta,f,ensure_ascii=False,indent=2)
            f.truncate()
            
    def get_metadata(self)-> Dict:
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r",encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    #File upload,vector_strore
    def file_process(self,file_path:str) -> bool:
        '''
        Process file with data pipi line
        '''
        if not os.path.exists(file_path):
            logger.error(f"Not found find upload {file_path}")
            return False

        dest_path = os.path.join(self.upload_dir,os.path.basename(file_path))
        shutil.copy(file_path,dest_path)
        self.current_path = dest_path
        logger.info(f" Copied file to {dest_path} \n Starting pipe line with {dest_path}")
        #Pipeline process 
        index_path, chunks = self.pipe_line.process(file_path=dest_path, save_dir=self.vector_dir)
        #loafd index -> retriever
        vt_store = self.vectore_store.load_vectore_store(
            save_dir=self.vector_dir,
            embedding_model= self.embedding_service
            
        )
        self.retriever = self.retriever_handler.build(
            vector_store= vt_store,
            all_docs= chunks
        )
        self.engine = RagEngine(retriever=self.retriever)
        #update meta data
        self.update_metadata(file_uploaded =True, file_name = os.path.basename(file_path))
        logger.info(f" file process and FAISS index strore at {index_path}")
        return True
    
    def ask(self,question:str)-> str:
        if not self.engine:
            return "I'm chat bot with document. Please upload document!!"
        try:
            self.memory.chat_memory.add_user_message(question)
            answer = self.engine.generate(question)
            self.memory.chat_memory.add_ai_message(answer)
            self.save_chat_history()
            return answer
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "Sorry, something went wrong."   
    
    def save_chat_history(self):
        path  = os.path.join(self.session_dir,"chat_history.json")
        try:
            data = [{'role':m.type,"content": m.content} for m in self.memory.chat_memory.messages]
            with open(path,"w",encoding="utf-8") as f:
                json.dump(data,f, ensure_ascii=False,indent=2)
                logger.info(f"Save chat history for session {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to save chat history {e}")
            
    def load_chat_history(self)->bool:
        path = os.path.join(self.session_dir,"chat_history.json")
        if not os.path.exists(path):
            logger.warning("Not found chat history")
            return False
        try:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
                for msg in data:
                    if msg['role'] =='human':
                        self.memory.chat_memory.add_user_message(msg['content'])
                    else:
                        self.memory.chat_memory.add_ai_message(msg['content'])
                return True
        except Exception as e:
            logger.error(f" Erro loading chat history {e}")
            return False
    
    def detete_session(self) -> bool:
        ''' Delete all session (upload,vt_store, history)'''
        try:
            if os.path.exists(self.session_dir):
                shutil.rmtree(self.session_dir,ignore_errors=True)
                logger.info(f" Deleted session folder {self.session_dir}")
                return True
            else:
                logger.warning(f"Session dir not found{self.session_dir}")
                return False
        except Exception as e:
            logger.error(f" Error deleting session {e}")
            return False
    
    from typing import Generator, Any

# =========================================================
# 💬 STREAMING CHAT
# =========================================================
    def stream_chat(self, question: str, placeholder: Any) -> Generator[str, None, None]:
        """
        Trả lời câu hỏi theo dạng stream (luồng dữ liệu),
        đồng thời hiển thị liên tục trên giao diện Streamlit.
        """
        if not self.engine:
            yield "No document uploaded. Please upload a document first."
            return

        try:
            self.memory.chat_memory.add_user_message(question)
            placeholder.markdown("🤔 *Thinking...*")

            #  Lấy các tài liệu liên quan
            docs = self.retriever_handler.get_relevant_documents(question)
            context = "\n\n".join([d.page_content for d in docs[: config.K_FINAL]])

            # Tạo prompt cho LLM
            prompt = self.engine.format_prompt(context=context, question=question)

            response = ""
            #tream output từ LLM
            for chunk in self.engine.llm.stream(prompt):
                text = getattr(chunk, "content", "")
                response += text
                placeholder.markdown(response)
                yield text

            # Lưu vào bộ nhớ hội thoại
            self.memory.chat_memory.add_ai_message(response)
            self.save_chat_history()

            yield "\n"
        except Exception as e:
            logger.error(f" Error during streaming chat: {e}")
            yield " Sorry, an error occurred during chat streaming."

    # =========================================================

    # =========================================================
    def clear_history(self):
        """Xóa toàn bộ lịch sử chat khỏi bộ nhớ."""
        self.memory.clear()
        logger.info("🧹 Cleared chat memory for session %s", self.session_id)
    
    @staticmethod
    def list_user_sessions(user_id:str ,base_dir:str="data/sessions") -> List[Dict]:
        
        user_dir = os.path.join(base_dir,f"user_{user_id}")
        if not os.path.exists(user_dir):
            return []
        sessions = []
        for folder in os.listdir(user_dir):
            meta_path = os.path.join(user_dir,folder,'metadata.json')
            if os.path.exists(meta_path):
                try:
                    with open(meta_path,"r",encoding='utf-8') as f:
                        meta = json.load(f)
                    meta.setdefault('title','Unitled')
                    meta["path"] = os.path.join(user_dir,folder)
                    sessions.append(meta)
                except Exception as e:
                    logger.error(f" Erro reading metadat from {folder}:{e}")
        sessions.sort(key= lambda x:x.get('created_at',""),reverse= True)
        return sessions

    def summarize_title(self,first_quesion:str = "New chat"):
        '''Update title for firest question'''
        try:
            k_max_word = 5
            words= first_quesion.split()
            title = " ".join(words[:k_max_word]).capitalize()
            self.update_metadata(title=title) 
            logger.info(f" update title for display")
            return title
        except Exception as e:
            logger.error(f'Erro sumarize title{e}')
            return None
        
    def load_engine_from_disk(self):
        '''
        Load engine lai
        '''
        meta = self.get_metadata()
        if not meta.get('file_uploaded'):
            logger.warning('f"Session {self.session_id} File not marked as uploaded')
            return False
        try:
            uploaded_files = os.listdir(self.upload_dir)
            if len(uploaded_files) != 1:
                logger.error(f" Cannot restroe engine for session{self.session_id}")
                return False
            original_filename = uploaded_files[0]
        except FileNotFoundError:
            logger.error(f" Upload dir not founf  {self.upload_dir}. Can't restore")
            return False
        original_file_path  = os.path.join(self.upload_dir,original_filename)
        vector_store_exists = os.path.exists(self.vector_dir) and any(os.scandir(self.vector_dir))
        if not vector_store_exists:
            logger.error(f" VEctor store not found  for session {self.session_id}. Can't not restore")
            return False
        try:
            logger.info(f" Restoring RAG Engine for session")            
            chunkhandler = ChunkHandler()
            loader = DataLoader()
            docs,file_type  = loader.load_file(file_path=original_file_path )
            chunks  = chunkhandler.split_documents(docs=docs,file_type= file_type)
            # Tai lai vector Store
            vt_store = self.vectore_store.load_vectore_store(
                    save_dir=self.vector_dir,
                    embedding_model=self.embedding_service
                )
            self.retriever = self.retriever_handler.build(vector_store=vt_store, all_docs=chunks)
            self.engine = RagEngine(retriever=self.retriever)
            logger.info(f"✅ RAG Engine for session {self.session_id} successfully restored.")
            return True
        except Exception as e:
            logger.error(f"Failed to reload RAG engine from disk for session {self.session_id}: {e}")
            self.engine = None
            return False
        
    
        
            
            