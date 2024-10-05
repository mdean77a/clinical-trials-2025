from flask import Flask, Response, request, stream_with_context
from flask_cors import CORS
import os
import time
app = Flask(__name__)
CORS(app)

# Create a directory to save uploaded files
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('pdf_files')
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        saved_files.append(file.filename)

    # Simulate processing time before streaming data
    def generate():
        # Simulate processing delay (e.g., 5 seconds)
        time.sleep(5)  # Adjust the delay as needed

        # Start streaming data
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
        # Simulate streaming by sending chunks with delays
        for chunk in data_chunks:
            yield chunk
            time.sleep(0.5)  # Simulate delay between chunks

    return Response(stream_with_context(generate()), mimetype='application/json')

@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json()
    field = data.get('field')
    content = data.get('content')
    question = data.get('question')
    # Simulate a response from an AI assistant
    response_content = f"Updated content for {field} based on question: {question}"
    return {'content': response_content}

if __name__ == '__main__':
    app.run(debug=True)
