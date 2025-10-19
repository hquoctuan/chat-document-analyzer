import os
from langchain_community.vectorstores import FAISS
from app.helper.logger import get_logger


logger = get_logger('VectorStore')

class VectorStore:
    ''' Quan ly build/ save/ laod Faiss vector store'''
    def build_vector_store(self,docs, embedding_model):
        try:
            vector_store = FAISS.from_documents(documents=docs, embedding=embedding_model )
            return vector_store
        except Exception as e:
            logger.error(f'Erro build vector store{e}')
            raise
    def save_vector_store(self,vector_store:FAISS, save_dir:str)-> str:
        try:
            os.makedirs(save_dir,exist_ok=True)
            index_path = os.path.join(save_dir,'faiss_index')
            vector_store.save_local(index_path)
            logger.info(f'FAISS saved in {index_path}')
            return index_path
        except Exception as e:
            logger.erro(f'Error save FAISS {e}')
            raise
    
    def load_vectore_store(self,save_dir:str, embedding_model):
        try:
            index_path = os.path.join(save_dir,'faiss_index')
            vector_store = FAISS.load_local(index_path,embeddings=embedding_model,allow_dangerous_deserialization=True)
            logger.info(f' Loaded FAISS index from {index_path}')
            return vector_store
        except Exception as e:
            logger.error(f'Erro load FAISS {e}')
            raise
        
         