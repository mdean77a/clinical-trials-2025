from typing import AsyncGenerator
from threading import Thread
import os
import time
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import json

from langserve import add_routes

from reportlab.pdfgen import canvas
from io import BytesIO
import markdown2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.qdrant_retriever import QdrantRetrieverClient

from app.config import Config
from app.agents import ClinicalTrialGraph
from app.rag_builder import RagBuilder
from app.filehandler import FileHandler
from app.pdf_loader_chunker import pdf_load_chunk
from langchain_core.messages import HumanMessage

app = FastAPI()
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


file_handler = FileHandler()
qdrant_retriever_client = QdrantRetrieverClient()
rag_builder = RagBuilder(qdrant_retriever_client)
clinical_trial_agents = ClinicalTrialGraph(rag_builder)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    file_status = file_handler.load_file_status()
    saved_files = []
    for file in files:
        file_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        saved_files.append(file_path)
        # Mark file as processing
        file_status[file.filename] = 'processing'
    file_handler.save_file_status(file_status)

    # We need to start the processing here 
    def process_files():
        time.sleep(5)
        file_status = file_handler.load_file_status()
        vectorstore = qdrant_retriever_client.get_vectorstore()
        for file_path in saved_files:
            try:
                docs = pdf_load_chunk(file_path)
                vectorstore.add_documents(docs)
                file_status[os.path.basename(file_path)] = 'processed'
            except Exception as e:
                file_status[os.path.basename(file_path)] = f'error: {str(e)}'
        file_handler.save_file_status(file_status)

    Thread(target=process_files).start()
    return JSONResponse({'message': 'Files uploaded and processing started.'})

@app.get("/existing-files")
async def get_existing_files():
    file_status = file_handler.load_file_status()
    files = [{'name': filename, 'status': status} for filename, status in file_status.items()]
    return JSONResponse({'files': files})

@app.post("/generate-consent-form")
async def generate_consent_form(request: Request):
    request_data = await request.json()
    files = request_data.get("files", [])
    file_names = [f["name"] for f in files if f.get("name")]
    print(f"Generating consent form for files: {file_names}")
    graph = ClinicalTrialGraph(rag_builder, file_names)
    
    async def response_generator():
        combined_output = {
            "summary": "",
            "background": "",
            "number_of_participants": "",
            "study_procedures": "",
            "alt_procedures": "",
            "risks": "",
            "benefits": ""
        }
        try:
            async for update in graph.astream():
                # print(f"Received update: {json.dumps(update)}")
                for key, value in update.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            combined_output[sub_key] = sub_value[0] if isinstance(sub_value, list) and sub_value else sub_value
                    else:
                        combined_output[key] = value[0] if isinstance(value, list) and value else value
                # print(f"{json.dumps(combined_output)}")
                # Yield the current state of combined_output
                yield json.dumps(combined_output)
        except Exception as e:
            yield json.dumps({'error': str(e)})
        
        # Yield the final combined output
        yield json.dumps(combined_output)

    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.post("/revise")
async def revise():
    return JSONResponse({'status': 'accepted'})

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
import re

def clean_text_for_pdf(text: str) -> str:
    if not text:
        return ""
    
    # Remove HTML tags and normalize whitespace
    cleaned = re.sub(r'<[^>]+>', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    # Split into paragraphs and filter empty lines
    paragraphs = [p.strip() for p in cleaned.split('\n') if p.strip()]
    
    return '\n\n'.join(paragraphs)

@app.post("/download-consent-pdf")
async def download_consent_pdf(request: Request):
    try:
        data = await request.json()
        if not data or 'data' not in data:
            return JSONResponse({"error": "No data provided"}, status_code=400)

        content = data['data']
        buffer = BytesIO()
        
        # Set up the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            title="Consent Form",
            leftMargin=72,  # 1 inch margins
            rightMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Customize styles
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            leading=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        normal_text_style = ParagraphStyle(
            'NormalText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica'
        )

        story = []

        def add_section(title: str, content: str):
            if not content:
                return
                
            # Add section title
            story.append(Paragraph(title.upper(), section_title_style))
            
            # Clean and process content
            cleaned_content = clean_text_for_pdf(content)
            
            # Split into paragraphs and add each
            for paragraph in cleaned_content.split('\n\n'):
                if paragraph.strip():
                    try:
                        story.append(Paragraph(paragraph.strip(), normal_text_style))
                    except Exception as e:
                        print(f"Error processing paragraph: {e}")
                        # Add as plain text if parsing fails
                        story.append(Paragraph(str(paragraph.strip()), normal_text_style))
            
            story.append(Spacer(1, 12))

        # Add document header
        story.append(Paragraph("CLINICAL TRIAL CONSENT FORM", styles['Heading1']))
        story.append(Spacer(1, 20))

        # Add all sections
        sections = [
            ("SUMMARY", content.get("summary", "")),
            ("BACKGROUND", content.get("background", "")),
            ("NUMBER OF PARTICIPANTS", content.get("number_of_participants", "")),
            ("STUDY PROCEDURES", content.get("study_procedures", "")),
            ("ALTERNATIVE PROCEDURES", content.get("alt_procedures", "")),
            ("RISKS", content.get("risks", "")),
            ("BENEFITS", content.get("benefits", ""))
        ]

        for title, text in sections:
            add_section(title, text)

        # Add signature section
        story.append(Spacer(1, 30))
        story.append(Paragraph("SIGNATURES", section_title_style))
        story.append(Spacer(1, 20))
        
        # Add signature lines
        signature_text = """
        Parent/Guardian Name: _______________________________
        
        Signature: _______________________________ Date: ____________
        
        Person Obtaining Consent: _______________________________
        
        Signature: _______________________________ Date: ____________
        """
        
        story.append(Paragraph(signature_text, normal_text_style))

        # Generate PDF
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type='application/pdf',
            headers={
                "Content-Disposition": "attachment; filename=consent_form.pdf",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return JSONResponse(
            {"error": f"Failed to generate PDF: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn



    uvicorn.run(app, host="0.0.0.0", port=8000)
