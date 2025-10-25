import os
import json
import time
import shutil
from typing import Optional, Dict, List
from app.handler.chat_handler import ChatHandler
from app.helper.logger import get_logger
from app.services.llama_service import GroqLlamaService

logger = get_logger('ChatSessionManager')

class ChatSessionManager:
    '''
    Quan ly nhieu cuoc hoi thoai song song cho 1 user
    '''
    
    def __init__(self, user_id: str, base_dir:str= "data/sessions"):
        self.user_id  = user_id
        self.base_dir = base_dir
        self.user_dir = os.path.join(base_dir,f"user{user_id}")
        os.makedirs(self.user_dir,exist_ok= True)
        self.active_session_id : Optional[str] = None
        self.sessions =  {}
        
    
    def create_session(self)->str:
        ''' Tao moi session va khoi tao ChatHanler'''
        session_id = str(time.time())
        session_path = os.path.join(self.user_dir,f"session_{session_id}")
        os.makedirs(session_path,exist_ok= True)
        handler = ChatHandler(user_id= self.user_id, base_dir= self.user_dir)
        self.sessions[session_id] = handler
        self.active_session_id = session_id
        #Meta_data
        meta = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": "New Chat",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"), 
            "file_uploaded": False                            
        }
        with open(os.path.join( session_path,"metadata.json"),"w", encoding="utf-8") as f:
            json.dump(meta,f,ensure_ascii= False, indent =2)
        
        logger.info(f"Create new session {session_id}")
        return session_id
    
    def load_session(self, session_id:str) -> Optional[ChatHandler]:
        ''' Load lai session cu tu meta'''
        session_path = os.path.join(self.user_dir,f"session_{session_id}")
        if not os.path.exists(session_path):
            logger.waring(f" Session {session_path} not found")
            return None
        
        hanlder = ChatHandler(user_id= self.user_id,session_id= session_id ,base_dir=self.user_dir)
        hanlder.session_id = session_id
        hanlder.session_dir = session_path
        hanlder.load_chat_history()
        
        self.sessions[session_id]= hanlder
        self.active_session_id  = session_id
        
        logger.info(f" Load existing session {session_id}")
        return hanlder
    
    


    def list_sessions(self) -> List[Dict]:
        """Trả về danh sách metadata của các phiên chat."""
        sessions_meta = []
        for folder in os.listdir(self.user_dir):
            session_path = os.path.join(self.user_dir, folder)
            meta_path = os.path.join(session_path, "metadata.json")

            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)

                    # Đảm bảo luôn có title và created_at
                    meta.setdefault("title", "Untitled Chat")
                    meta.setdefault("created_at", os.path.getctime(session_path))

                    sessions_meta.append(meta)
                except Exception as e:
                    logger.error(f"❌ Error reading metadata for {folder}: {e}")

        # Sắp xếp mới nhất lên đầu
        sessions_meta.sort(key=lambda x: x["created_at"], reverse=True)
        return sessions_meta

    

    def delete_session(self,session_id:str)-> bool:
        ''' Xoa toan bo du lieu cua 1 session'''
        session_path = os.path.join(self.user_dir,f"session_{session_id}")
        if not os.path.exists(session_path):
            return False
        
        shutil.rmtree(session_path,ignore_errors=True)
        self.sessions.pop(session_id,None)
        if self.active_session_id == session_id:
            self.active_session_id = None
        logger.info(f" Delete session {session_id}")
        return True
    
    def summarize_title(self, session_id: str, first_question: str):
        ''' Create title for chat '''
        try:
            # Giả sử GroqLlamaService là một class có sẵn
            # from your_services import GroqLlamaService 
            max_words = 5
            all_words = first_question.split()
            title_words = all_words[:max_words]
            title = " ".join(title_words)

            
            meta_path = os.path.join(self.user_dir, f"session_{session_id}", "metadata.json")
            
            if os.path.exists(meta_path):
                # 'r+' cho phép đọc và ghi file
                with open(meta_path, "r+", encoding="utf-8") as f:
                    meta = json.load(f)
                    meta['title'] = title.strip()
                    
                    f.seek(0) # Di chuyển con trỏ về đầu file để ghi đè
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                    f.truncate() # Xóa nội dung thừa nếu file mới ngắn hơn file cũ
            
            logger.info(f"Updated title for session {session_id}")
        
        except Exception as e:
            # Thêm biến 'e' vào log để biết lỗi chi tiết
            logger.warning(f"Can't summarize for chat session {session_id}: {e}")
    

                     
        
    
        
        
        
        
    
    
        
                


