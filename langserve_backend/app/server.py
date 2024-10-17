from operator import itemgetter
from typing import Any
import time

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from langserve import add_routes
from langserve import add_routes


from langchain_openai import ChatOpenAI
from langserve import add_routes
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from .rag_builder import RagBuilder
from .filehandler import FileHandler

app = FastAPI()

file_handler = FileHandler()
rag_builder = RagBuilder()

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, NotImplemented)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
