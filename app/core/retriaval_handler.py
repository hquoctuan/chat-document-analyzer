from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from sentence_transformers import CrossEncoder
from langchain.vectorstores.base import VectorStoreRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from app.config import config
from app.helper.logger import get_logger
logger = get_logger("RetrivalHandler")

class RetrivalHandler:
    
    def __init__(self):
        ''' Handler de quan li cac loai retriver '''
        self.type_use = config.TYPE_RETRIEVAL
        self.k_bm25 = config.K_BM25
        self.k_vector  = config.K_VECTOR
        #self.weight = config.WEIGHT_RERANK
        self.weight = [0.5, 0.5]
        self.rerank_enable = config.ENABLE
        self.k_final = config.K_FINAL
        self.rerank_model = config.RERANKER_MODEL
    

        
    def build(self, vector_store, all_docs = None):
        
        """
        vectorstore: FAISS đã build (LangChain VectorStore)
        all_docs: list[Document] toàn bộ docs đã index (cần cho BM25)
        """
        try:
            if self.type_use =='hybrid':
                if all_docs  is None:
                    logger.warning("Hybrid mode: all docs is None  -> BM25 not action. Fall back dense only  ")
                    return self._dense_only(vector_store)
                bm25 = BM25Retriever.from_documents(all_docs)
                dense  = vector_store.as_retriever(search_kwargs={"k": self.k_vector})
                
                base = EnsembleRetriever(retrievers=[bm25,dense],weights=self.weight)
                
            else:
                base = self._dense_only(vector_store)
            
            if self.rerank_enable:
                cross_model = HuggingFaceCrossEncoder(model_name=self.rerank_model)
                reranker = CrossEncoderReranker(model=cross_model, top_n=self.k_final)
                retriever = ContextualCompressionRetriever(
                    base_compressor= reranker,
                    base_retriever= base
                    
                )
                logger.info(f" Rerank enable ({self.rerank_model}) ,(k_final: {self.k_final})")
                return retriever
            
            logger.info(f"Rerank disable. Using base retriver")
            return base

        except Exception as e:
            logger.error(f"Erro building retriever {e}") 
            return self._dense_only(vector_store)

    
    def _dense_only(self,vector_store) -> VectorStoreRetriever:
        dense = vector_store.as_retriever(search_kwargs={"k":self.k_vector})
        logger.info(f" Dense only  retriever (k_vector {self.k_vector})")
        return dense





        
        
        

    
 



