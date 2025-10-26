from langchain_huggingface import HuggingFaceEmbeddings
from app.helper.logger import get_logger
import time 
from app.config import config


logger = get_logger("Calling Embedding Service")

class EmbeddingService:
    ''' Serivce quan li va cung cap embedding tu Hugging Face'''
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingService,cls).__new__(cls)
            cls._instance._initalize_model()
        return  cls._instance
    
    def _initalize_model(self):
        start_time = time.time()
        try:
            model_name =  config.EMBEDDING_MODEL
            model_kwargs = {"device": "cpu"}
            encode_kwargs = {"normalize_embeddings": False}
            self.model = HuggingFaceEmbeddings(
            model_name =model_name,
            model_kwargs = model_kwargs,
            encode_kwargs =encode_kwargs)
            logger.info(f"Embedding model {model_name} laoding successfull: (time: {time.time()-start_time:.2f})")
            
        except Exception as e:
            logger.error(f"Fail call initalize moodel {model_name} (time: {time.time()-start_time:.2f})s")
            raise
    
    def embed_text(self,text:str):
        '''  Return ebedding cho mot doan text don le'''
        try:
            embedding = self.model.embed_query(text)
            logger.info(f"Generated embedding for text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f" Erro generate embeeding for text {e}")
            raise
    
    def embed_documents(self, documents: list[str]):
        ''' Return ve embedding cho nhieu doan text'''
        try: 
            logger.info(f" Generating embeddding for {len(documents)} document")
            embeddings = self.model.embed_documents(documents)
            logger.info(f"Successfully generated {len(embeddings)} embeddings.")
            return embeddings
        except Exception as e:
            logger.error(f" Erro generate embeeding for text {e}")
            raise

embedder = EmbeddingService()
vector = embedder.embed_text("Xin chào, đây là câu test embedding.")
