from operator import itemgetter

from langchain.schema.output_parser import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .templates import rag_prompt_template
from .config import Config
from .qdrant_retriever import QdrantRetrieverClient


class RagBuilder:
    def __init__(self, retriever_client: QdrantRetrieverClient = None):        
        self.retriever_client = retriever_client if retriever_client else QdrantRetrieverClient()
        self.retriever = self.retriever_client.get_retriever()
        self.llm = ChatOpenAI(model=Config.OPENAI_MODEL_NAME, streaming=True, temperature=0)
        self.rag_prompt = ChatPromptTemplate.from_template(rag_prompt_template)
        self.rag_chain = self.__build_chain()

    def __build_chain(self, filtered : bool = False):
        if filtered:
            return (
                {"context": itemgetter("question") | self.retriever, "question": itemgetter("question")}
                | self.rag_prompt | self.llm | StrOutputParser()
            )
        else:
            return (
                {"context": itemgetter("question") | self.retriever, "question": itemgetter("question")}
                | self.rag_prompt | self.llm | StrOutputParser()
            )
        
