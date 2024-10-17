from typing import List
import logging

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import Config

def pdf_load_chunk(file_path: str) -> List[Document]:
    """
    Load a PDF file, concatenate its pages, and split the content into chunks.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        List[Document]: List of Document objects containing the text chunks.
    """
    # Load PDF pages
    loader = PyMuPDFLoader(file_path)
    separate_pages = loader.load()
    logging.info(f"Number of separate pages: {len(separate_pages)}")

    # Concatenate all pages into a single document string
    document_string = "".join(page.page_content for page in separate_pages)
    logging.info(f"Length of the document string: {len(document_string)}")

    # Define a function to calculate the length of text in tokens
    def tiktoken_len(text: str) -> int:
        tokens = tiktoken.encoding_for_model(Config.OPENAI_MODEL_NAME).encode(text)
        return len(tokens)

    # Split the document string into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=tiktoken_len
    )
    text_chunks = text_splitter.split_text(document_string)
    logging.info(f"Number of chunks: {len(text_chunks)}")

    # Create Document objects for each chunk
    documents = []
    for index, chunk in enumerate(text_chunks):
        documents.append(Document(
            page_content=chunk,
            metadata={"chunk_index": index, "document_title": file_path.split("/")[-1]}
        ))
    logging.info(f"Length of document: {len(documents)}")

    return documents
