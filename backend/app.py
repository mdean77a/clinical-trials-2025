import os
import time
import json
from threading import Thread, Lock
from flask import Flask, Response, request, stream_with_context, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('pdf_files')
    file_status = load_file_status()
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        # Mark file as processing
        file_status[file.filename] = 'processing'
    save_file_status(file_status)
    # Simulate processing delay
    def process_files():
        time.sleep(5)
        file_status = load_file_status()
        for file in files:
            file_status[file.filename] = 'processed'
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

@app.route('/generate-consent-form', methods=['POST'])
def generate_consent_form():
    data = request.get_json()
    files = data.get('files', [])
    # Start background processing
    def process_consent_form():
        # Simulate processing delay
        time.sleep(2)
        # Simulate generated data
        consent_form_data['content'] = {
            'summary': 'This study aims to investigate...',
            'background': 'Chronic illness affects millions...',
            'numberOfParticipants': 'Approximately 500 participants...',
            'studyProcedures': 'Participants will undergo tests...',
            # Add other fields as needed
        }
    Thread(target=process_consent_form).start()
    return jsonify({'status': 'accepted'})

@app.route('/consent-form-stream', methods=['GET'])
def consent_form_stream():
    def generate():
        while 'content' not in consent_form_data:
            time.sleep(1)
        # Stream the consent form data as JSON chunks
        data = consent_form_data['content']
        json_data = json.dumps(data)
        # Simulate streaming by sending chunks
        chunk_size = 50
        for i in range(0, len(json_data), chunk_size):
            chunk = json_data[i:i+chunk_size]
            yield chunk
            time.sleep(0.5)
    return Response(stream_with_context(generate()), mimetype='application/json')

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
