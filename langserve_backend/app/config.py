import os
from decouple import config

class Config:
    OPENAI_API_KEY = config('OPENAI_API_KEY')
    COLLECTION_NAME = config('COLLECTION_NAME')
    QDRANT_URL = config('QDRANT_URL')
    OPENAI_MODEL_NAME = config('OPENAI_MODEL_NAME')
    OPENAI_EMBEDDING_MODEL_NAME = config('OPENAI_EMBEDDING_MODEL_NAME')
    OPENAI_EMBEDDING_MODEL_DIMENSION = config('OPENAI_EMBEDDING_MODEL_DIMENSION')
    LANGCHAIN_PROJECT = config('LANGCHAIN_PROJECT')
    LANGCHAIN_TRACING_V2 = config('LANGCHAIN_TRACING_V2')
    LANGCHAIN_ENDPOINT = config('LANGCHAIN_ENDPOINT')    
    UPLOAD_FOLDER = f"{os.path.dirname(os.path.abspath(__file__))}/{config('UPLOAD_FOLDER')}"
    PROCESSED_FOLDER = f"{os.path.dirname(os.path.abspath(__file__))}/{config('PROCESSED_FOLDER')}"
    CACHE_DIR = f"{os.path.dirname(os.path.abspath(__file__))}/{config('CACHE_DIR')}"
    DB_FILE = f"{os.path.dirname(os.path.abspath(__file__))}/{config('DB_FILE')}"
    CHUNK_SIZE=config('CHUNK_SIZE')
    CHUNK_OVERLAP=config('CHUNK_OVERLAP')

    @staticmethod
    def ensure_directories():
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.PROCESSED_FOLDER, exist_ok=True)
        os.makedirs(Config.CACHE_DIR, exist_ok=True)

# Ensure directories are created when the module is imported
Config.ensure_directories()

    