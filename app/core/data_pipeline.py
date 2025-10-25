import os
from app.core.chunk_handler import ChunkHandler
from app.core.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService
from app.core.data_loader import DataLoader
from app.helper.logger import get_logger

# Khởi tạo logger
logger = get_logger('PipelineRAG')

# -----------------------------------------------------

class DataPipeLine:
    """Class đại diện cho luồng xử lý dữ liệu (ETL) để xây dựng Vector Store cho RAG."""

    def __init__(self):
        """Khởi tạo các thành phần xử lý dữ liệu."""
        self.loader = DataLoader()
        self.chunk = ChunkHandler()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        
        
    def process(self, file_path: str, save_dir: str = 'data/vector_store') -> str:
        """
        Thực thi luồng chạy cho pipeline RAG.

        Args: 
            file_path: Đường dẫn tới file CSV hoặc PDF.
            save_dir: Nơi lưu trữ FAISS index.

        Return: Đường dẫn (path) đến FAISS index đã lưu.
        """
        try:
            logger.info(f"Starting data pipe line for file: {file_path}")

            # Step 1: Load file 
            docs, file_type = self.loader.load_file(file_path)
            logger.info(f"Loaded {len(docs)} documents of type: {file_type}")
            
            # Step 2: Chunk Document
            chunks = self.chunk.split_documents(docs=docs, file_type=file_type)
            logger.info(f'Split into {len(chunks)} chunks')
            
            # Step 3: Build Embedding model 
            embedding_model = self.embedding_service.model
            logger.info(f'Using embedding model: {self.embedding_service.model.model_name}')
            
            # Step 4: Build Vector Store
            vectorstore = self.vector_store.build_vector_store(chunks, embedding_model=embedding_model)
            logger.info('FAISS vector store built successfully')
            
            # Step 5: Save Vector Store
            os.makedirs(save_dir, exist_ok=True)
            index_path = self.vector_store.save_vector_store(vector_store=vectorstore, save_dir=save_dir)
            logger.info(f'Vector Store saved at: {index_path}') # Đã sửa logger info thành index_path

            logger.info('Pipeline completed successfully')
            return index_path, chunks
        
        except Exception as e:
            logger.error(f'Failed to build pipeline: {e}')
            raise

if __name__ =="__main__":
    pipeline =DataPipeLine()
    index_path ='data/laptop.csv'
    pipeline.process(index_path)
    print(f"Done. Index saved at: {index_path}")
    