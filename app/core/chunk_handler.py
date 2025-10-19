import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from app.config import config
from app.helper.logger import get_logger

logger = get_logger("ChunkHandler")


class ChunkHandler:
    """Handle splitting of documents (PDF or CSV) into smaller semantic chunks for RAG."""

    def __init__(self):
        self.default_chunk_size = config.CHUNK_SIZE
        self.default_chunk_overlap = config.CHUNK_OVERLAP

    # -------------------------------------------------------
    # Main interface
    # -------------------------------------------------------
    def split_documents(self, docs: list[Document], file_type: str) -> list[Document]:
        """
        Split documents into chunks based on file type.

        Args:
            docs (list[Document]): List of documents loaded by DataLoader
            file_type (str): Either 'pdf' or 'csv'

        Returns:
            list[Document]: List of chunked documents
        """
        splitter = self.get_splitter(file_type)

        if splitter == "csv":
            logger.info("🧩 Using CSV chunking strategy.")
            return self._split_csv_docs(docs)
        elif isinstance(splitter, RecursiveCharacterTextSplitter):
            logger.info("📘 Using text splitter for PDF or text-like content.")
            return splitter.split_documents(docs)
        else:
            logger.warning(f"⚠️ Unknown splitter for file_type={file_type}. Defaulting to text splitter.")
            fallback = self._get_pdf_splitter()
            return fallback.split_documents(docs)

    # -------------------------------------------------------
    # Splitter selector
    # -------------------------------------------------------
    def get_splitter(self, file_type: str):
        """
        Return appropriate splitter based on normalized file type ('pdf' or 'csv')
        """
        file_type = file_type.lower().strip()
        if file_type == "pdf":
            logger.info("Selected PDF splitter.")
            return self._get_pdf_splitter()
        elif file_type == "csv":
            logger.info("Selected CSV splitter.")
            return "csv"
        else:
            logger.warning(f"Unrecognized file type '{file_type}'. Defaulting to PDF splitter.")
            return self._get_pdf_splitter()

    # -------------------------------------------------------
    # PDF Splitter
    # -------------------------------------------------------
    def _get_pdf_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create a recursive splitter for PDF or long text documents."""
        logger.info("Initializing RecursiveCharacterTextSplitter for PDF.")
        return RecursiveCharacterTextSplitter(
            chunk_size=self.default_chunk_size,
            chunk_overlap=self.default_chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    # -------------------------------------------------------
    # CSV Chunker
    # -------------------------------------------------------
    def _split_csv_docs(self, docs: list[Document], group_size: int = 2) -> list[Document]:
        """
        Group multiple CSV rows (each row = 1 Document) into larger chunks.
        This helps LLM understand structured data better.

        Args:
            docs (list[Document]): List of CSV row documents
            group_size (int): How many rows to group per chunk
        """
        all_chunks = []
        try:
            grouped_texts = [
                "\n".join([doc.page_content for doc in docs[i:i + group_size]])
                for i in range(0, len(docs), group_size)
            ]

            for chunk_text in grouped_texts:
                all_chunks.append(Document(page_content=chunk_text))

            logger.info(f"📊 CSV grouped into {len(all_chunks)} chunks (each ~{group_size} rows).")
            return all_chunks

        except Exception as e:
            logger.exception(f"❌ Error while grouping CSV documents: {e}")
            raise
