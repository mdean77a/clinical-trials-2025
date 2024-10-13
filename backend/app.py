import os
import uuid
from dotenv import load_dotenv
import time
import json
from threading import Thread, Lock
from flask import Flask, Response, request, stream_with_context, jsonify
from flask_cors import CORS

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams,Filter, FieldCondition, MatchValue
from langchain.storage import LocalFileStore
from langchain_qdrant import QdrantVectorStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from operator import itemgetter
from langchain_core.runnables.passthrough import RunnablePassthrough
from qdrant_client.http.exceptions import UnexpectedResponse

app = Flask(__name__)
CORS(app)

load_dotenv()

os.environ["LANGCHAIN_PROJECT"] = "Clinial Trials"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Create necessary directories
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# File to store the status of files
DB_FILE = 'file_status.json'

# Lock for thread-safe file access
file_status_lock = Lock()

def load_file_status():
    with file_status_lock:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                file_status = json.load(f)
        else:
            file_status = {}
    return file_status

def save_file_status(file_status):
    with file_status_lock:
        with open(DB_FILE, 'w') as f:
            json.dump(file_status, f)

# In-memory storage for consent form data and revision data
consent_form_data = {}
revision_data = {}

# Dummy data for now
consent_form_data['content'] = {
            'summary': 'This study aims to investigate...',
            'background': 'Chronic illness affects millions...',
            'numberOfParticipants': 'Approximately 500 participants...',
            'studyProcedures': 'Participants will undergo tests...',
            # Add other fields as needed
        }


##  AI Prompts
rag_system_prompt_template = """\
You are a helpful assistant that uses the provided context to help generate clinical trials consent documentation in json format. 

"""

rag_message_list = [
    {"role" : "system", "content" : rag_system_prompt_template},
]

rag_user_prompt_template = """\
Question:
{question}
Context:
{context}
"""

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", rag_system_prompt_template),
    ("human", rag_user_prompt_template)
])

# LLM Models
chat_model = ChatOpenAI(model="gpt-4o-mini")
# Typical Embedding Model
core_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


# File Loader 
Loader = PyMuPDFLoader

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# Using locally running Qdrant
client = QdrantClient(url="http://localhost:6333")
collection_name = "clinical_trials"

def create_collection():
    try:
        # Check if the collection exists
        client.get_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' already exists. Using existing collection.")
    except UnexpectedResponse:
        # If the collection does not exist, create it
        print(f"Collection '{collection_name}' does not exist. Creating new collection.")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
    return client

def get_vectorstore_retriever():
    client = create_collection()
    
    # Adding cache!
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(current_dir, 'cache')
    os.makedirs(cache_dir, exist_ok=True)

    store = LocalFileStore(cache_dir)
    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        core_embeddings, store, namespace=core_embeddings.model
    )
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=cached_embedder)
    
    return vectorstore, vectorstore.as_retriever()

def get_filtered_retriever(files):
    vectorstore, retriever = get_vectorstore_retriever()
    filter_condition = Filter(
        must=[
            FieldCondition(
                key="filename",
                match=MatchValue(value=file_name.get('name').split('/')[-1])
            ) for file_name in files
        ]
    )
    # Create the retriever with the filter
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "filter": filter_condition,
            "k": 10  # Number of documents to retrieve
        }
    )
    return retriever

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('pdf_files')
    file_status = load_file_status()
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        saved_files.append(file_path)
        # Mark file as processing
        file_status[file.filename] = 'processing'
    save_file_status(file_status)
    
    # We need to start the processing here 
    def process_files():
        time.sleep(5)
        file_status = load_file_status()
        vectorstore, retriever = get_vectorstore_retriever()
        for file_path in saved_files:
            try:
                loader = Loader(file_path)
                documents = loader.load()
                docs = text_splitter.split_documents(documents)
                for i, doc in enumerate(docs):
                    doc.metadata["source"] = f"source_{i}"
                vectorstore.add_documents(docs)
                file_status[os.path.basename(file_path)] = 'processed'
            except Exception as e:
                file_status[os.path.basename(file_path)] = f'error: {str(e)}'
        save_file_status(file_status)

    Thread(target=process_files).start()
    return jsonify({'message': 'Files uploaded and processing started.'})

@app.route('/existing-files', methods=['GET'])
def get_existing_files():
    file_status = load_file_status()
    files = []
    for filename, status in file_status.items():
        files.append({'name': filename, 'status': status})
    return jsonify({'files': files})

# We need to call the agentic rag solution here 
@app.route('/generate-consent-form', methods=['POST'])
def generate_consent_form():
    data = request.get_json()
    files = data.get('files', [])
    print(files)
    retriever = get_filtered_retriever(files)

    retrieval_augmented_qa_chain = (
            {"context": itemgetter("question") | retriever, "question": itemgetter("question")}
            | RunnablePassthrough.assign(context=itemgetter("context"))
            | chat_prompt | chat_model
        )

    for chunk in retrieval_augmented_qa_chain.stream({"question": "generate clinical trials consent documentation"}):
        return jsonify(chunk)

@app.route('/revise', methods=['POST'])
def revise():
    data = request.get_json()
    field = data.get('field')
    content = data.get('content')
    question = data.get('question')
    # Start background processing for revision
    def process_revision():
        # Simulate processing delay
        time.sleep(2)
        # Simulate revised content
        revision_data[field] = f"Revised content for {field} based on question: {question}"
    Thread(target=process_revision).start()
    return jsonify({'status': 'accepted'})

@app.route('/revise-stream', methods=['GET'])
def revise_stream():
    field = request.args.get('field')
    def generate():
        while field not in revision_data:
            time.sleep(1)
        # Stream the revised content
        content = revision_data[field]
        # Simulate streaming by sending chunks
        chunk_size = 50
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            yield chunk
            time.sleep(0.5)
    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
