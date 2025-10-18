from app.helper.logger import get_logger
from langchain_text_splitters import (    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,)

from app.config import config


logger = get_logger('ChunkHandler')
class ChunkHandler:
    def __init__(self):
        self.default_chunk_size = config.CHUNK_SIZE
        self.defaul_chunk_over_lap = config.CHUNK_OVERLAP
        
        
        