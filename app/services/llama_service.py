from app.helper.config import config
from app.helper.logger import get_logger
from langchain.schema import HumanMessage
from langchain.chat_models import init_chat_model

import os 

import requests

logger = get_logger("llama_service")

class GroqLlamaService:
    ''' Service se goi groq API de truy van Llama model '''
    def __init__(self):
        groq_api_key = config.GROQ_API_KEY

        if not groq_api_key:
            
            raise ValueError("GROQ_API_KEY not found. Please set it in Streamlit secrets.")

        os.environ["GROQ_API_KEY"] = groq_api_key
        
        #if not os.environ.get("GROQ_API_KEY"):
            #os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY
        #self.api_key = config.GROQ_API_KEY
        self.model_name = config.LLM_MODEL
        self.temperature = config.TEMPERATURE
        self.max_tokens = config.MAX_TOKENS
        # khoi tao model Groq
        self.llm  = init_chat_model(
            model= self.model_name,
            model_provider='groq',
            temperature = self.temperature,
            max_tokens = self.max_tokens
        )
        logger.info(f" => GroqLlamaService initialized with model: {self.model_name}")

    def generate (self, promt:str)-> str:
        " Gui prompt va nhan phan hoi tu Groq LLama"
        try:
            logger.info(f" Prompt input  {promt[:100]}...")
            result = self.llm.invoke([HumanMessage(content=promt)])
            logger.info(f" Groq repone recived ({len(result.content)} chars)")
            return result.content
        
        except Exception as e:
            logger.error(f" Erro calling API {e}")
            raise
        
    def get_llm(self):
        return self.llm
    

if __name__ == "__main__":
    service = GroqLlamaService()
    answer = service.generate("The capital of Vieitnamese?")
    print("💬 Model Answer:\n", answer)
    
        