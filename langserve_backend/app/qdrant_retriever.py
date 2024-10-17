from typing import List
from langchain_qdrant import QdrantVectorStore
from langchain_core.vectorstores import VectorStoreRetriever
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    MatchAny,
    Filter,
    FieldCondition,
    MatchValue,
)
from .config import Config

class QdrantRetrieverClient:
    def __init__(self, collection_name: str = Config.QDRANT_COLLECTION_NAME):
        """ Initialize the Qdrant client and create the collection if it does not exist. """
        self.client = QdrantClient(url=Config.QDRANT_URL)
        self.collection_name = collection_name

        if not self.client.collection_exists(collection_name=self.collection_name):
            print(
                f"Collection '{self.collection_name}' does not exist. Creating new collection."
            )
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=Config.OPENAI_EMBEDDING_MODEL_DIMENSION, distance=Distance.COSINE
                ),
            )

    def get_retriever(self) -> VectorStoreRetriever:
        """ Create and return a VectorStoreRetriever. """
        qdrant_vectorstore = QdrantVectorStore(
            client=self.client, collection_name=self.collection_name, embedding=Config.OPENAI_EMBEDDING_MODEL_NAME
        )
        return qdrant_vectorstore.as_retriever()

    def get_retriever_with_filter(self, document_titles: List[str]) -> VectorStoreRetriever:
        """ Create and return a VectorStoreRetriever with a filter applied. """
        qdrant_vectorstore = QdrantVectorStore(
            client=self.client, collection_name=self.collection_name, embedding=Config.OPENAI_EMBEDDING_MODEL_NAME
        )
        
        retriever = qdrant_vectorstore.as_retriever(
            search_kwargs={
                'filter': Filter(
                    must=[
                        FieldCondition(
                            key="metadata.document_title",
                            match=MatchAny(any=document_titles)
                        )
                    ]
                ),
                'k': 15,                                       
            }
        )
        return retriever
