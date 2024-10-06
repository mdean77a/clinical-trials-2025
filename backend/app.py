import os
import time
import json
from dotenv import load_dotenv
from flask import Flask, Response, request, stream_with_context
from flask_cors import CORS
from flask import jsonify
from flask_cors import CORS

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain_qdrant import QdrantVectorStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)
CORS(app)
load_dotenv()
# Create a directory to save uploaded files
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# LLM Model 
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1024,
    chunk_overlap = 100,
    length_function = len,
)

qdrant_client = QdrantClient(":memory:")

# Adding cache!
store = LocalFileStore("./cache/")
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    embedding_model, store, namespace=embedding_model.model
)



app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
DB_FILE = 'file_status.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load or initialize file status database
if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r') as f:
        file_status = json.load(f)
else:
    file_status = {}

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('pdf_files')
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # Mark file as processing
        file_status[file.filename] = 'processing'
    save_file_status()
    # Simulate processing delay
    time.sleep(5)
    # Mark files as processed
    for file in files:
        file_status[file.filename] = 'processed'
    save_file_status()
    return jsonify({'message': 'Files uploaded and processing started.'})

@app.route('/existing-files', methods=['GET'])
def get_existing_files():
    files = []
    for filename, status in file_status.items():
        files.append({'name': filename, 'status': status})
    return jsonify({'files': files})

@app.route('/consent-form', methods=['POST'])
def consent_form():
    data = request.get_json()
    files = data.get('files', [])

    def generate():
        # Simulate processing delay
        time.sleep(2)
        data_chunks = [
            '{"summary": "This study aims to ',
            'investigate the effects of a new ',
            'drug on patients with chronic',
            ' illness.", "background": "Chronic ',
            'illness affects millions of people ',
            'worldwide. This study...", "numberOfParticipants": "The study will include ',
            'approximately 500 participants',
            ' across multiple sites.", ',
            '"studyProcedures": "Participants ',
            'will undergo a series of tests over ',
            'a period of 6 months..."',
            '}'
        ]
        for chunk in data_chunks:
            yield chunk
            time.sleep(0.5)
    return Response(stream_with_context(generate()), mimetype='application/json')

@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json()
    field = data.get('field')
    content = data.get('content')
    question = data.get('question')
    # Simulate AI response
    response_content = f"Updated content for {field} based on question: {question}"
    return jsonify({'content': response_content})

def save_file_status():
    with open(DB_FILE, 'w') as f:
        json.dump(file_status, f)

if __name__ == '__main__':
    app.run(debug=True)