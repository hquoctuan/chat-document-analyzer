import os
from langchain.docstore.document import Document
from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from app.helper.logger import get_logger

logger = get_logger("DataLoader")

class DataLoader:
    """Read PDF or CSV files and return a list of LangChain Document objects."""

    @staticmethod
    def load_file(file_path: str)-> tuple[list[Document],str]:
        """Main method: determine file type and load content."""
        if not os.path.exists(file_path):
            logger.error(f" File not found: {file_path}") 
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.endswith(".pdf"):
            docs = DataLoader._load_pdf(file_path)
            type_docs = "pdf"
        elif file_path.endswith(".csv"):
            docs = DataLoader._load_csv(file_path)
            type_docs ="csv"
        else:
            logger.error(f"❌ Unsupported file type: {file_path}")
            raise ValueError("Unsupported file type. Only PDF or CSV files are allowed.")

        logger.info(f"Successfully loaded file: {file_path}")
        return docs,type_docs

    @staticmethod
    def _load_pdf(file_path: str) -> list[Document]:
        """Load PDF file using LangChain's PyPDFLoader."""
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            logger.info(f" Loaded {len(docs)} pages from PDF: {os.path.basename(file_path)}")
            return docs
        except Exception as e:
            logger.exception(f" Error loading PDF file {file_path}: {e}")
            raise

    @staticmethod
    def _load_csv(file_path: str) -> list[Document]:
        """Load CSV file using LangChain's CSVLoader."""
        try:
            loader = CSVLoader(
                file_path=file_path,
                encoding="utf-8",
                csv_args={"delimiter": ",", "quotechar": '"'},
            )
            docs = loader.load()
            logger.info(f" Loaded {len(docs)} rows from CSV: {os.path.basename(file_path)}")
            return docs
        except Exception as e:
            logger.exception(f"❌ Error loading CSV file {file_path}: {e}")
            raise
