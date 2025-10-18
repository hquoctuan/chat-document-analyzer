from app.services.llama_service import GroqLlamaService
from app.services.embedding_service import EmbeddingService
from app.helper.logger import get_logger
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA

logger = get_logger('Core_Engine')

class RagEngine:
    def __init__(self,retriver = None):
        ''' RAG Engine core logic cho truy van retriver  va LLm'''
        self.llm_service = GroqLlamaService()
        self.llm = self.llm_service.llm
        self.embedding = EmbeddingService()
        self.retriver = retriver
        
        self.promt = PromptTemplate(
            template = (
            "You are an intelligent assistant. "
            "Answer the question clearly and accurately based only on the context below.\n\n"
            "=== Context ===\n{context}\n\n"
            "=== Question ===\n{question}\n\n"
            "Respond in the same language as the question, using a natural and concise tone."),
            input_variables=['context','question'],
        )
        
    
    def gernerate(self, question: str)-> str:
        if not self.retriver:
            logger.warning("Haven't retriver, use only LLM ")
            return self.llm_service.generate(question)
        try:
            logger.info(f" Generatin answer for quere {question[:100]}")
            qa_chain = RetrievalQA.from_chain_type(
                llm= self.llm,
                retriever = self.retriver,
                chain_type= 'stuff',
                chain_type_kwargs={"promt":self.promt},
                return_source_document = True
                  
            )
            result = qa_chain.invoke({"question": question})
            answer = result.get("result","")
            sources= result.get('source_document', [])
            logger.info(f" Answer generated ({len(answer)} chars, len{len(sources)})")
            if sources:
                for i, doc in enumerate(sources[:2]):
                    snippet = doc.page_content[:80].replace("\n", " ")
                    logger.info(f"Source {i+1}: {snippet}...")
                    
            return answer
        except Exception as e:
            logger.info(f"Error during RAG generation {e}")
            return "Sorry, an error occurred while generating the answer."
        
            
        
       
rag = RagEngine()
print(rag.gernerate("What is the capital in Korea"))

    