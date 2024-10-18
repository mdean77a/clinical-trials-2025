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
    allow_origins=["http://localhost:5173"],
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
                print(f"Received update: {json.dumps(update)}")
                for key, value in update.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            combined_output[sub_key] = sub_value[0] if isinstance(sub_value, list) and sub_value else sub_value
                    else:
                        combined_output[key] = value[0] if isinstance(value, list) and value else value
                
                # Yield the current state of combined_output
                yield f"data: {json.dumps(combined_output)}\n\n"
        except Exception as e:
            print(f"Error in stream: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        # Yield the final combined output
        yield f"data: {json.dumps(combined_output)}\n\n"

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

@app.post("/download-consent-pdf")
async def download_consent_pdf(request: Request):
    data = await request.json()
    if not data or 'data' not in data:
        return JSONResponse({"error": "No data provided"}, status_code=400)

    content = data['data']
    buffer = BytesIO()
    
    # Set up the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="Consent Form")
    styles = getSampleStyleSheet()
    
    # Customize styles for better presentation
    section_title_style = ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        spaceAfter=10,
        textColor=colors.darkblue,
        fontSize=14,
        leading=16
    )
    
    normal_text_style = ParagraphStyle(
        name="NormalText",
        parent=styles["BodyText"],
        fontSize=12,
        leading=14,
        spaceAfter=10
    )

    story = []

    # Function to add sections with headers and content
    def add_section(title, content):
        if content.strip():
            # Add title
            story.append(Paragraph(title, section_title_style))
            story.append(Spacer(1, 10))

            # Convert Markdown to HTML and then to PDF Paragraphs
            html_content = markdown2.markdown(content)
            paragraphs = html_content.split('\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, normal_text_style))
            story.append(Spacer(1, 15))

    # Adding sections with content
    add_section("Parental Permission, Teen Assent and Authorization Document", "")
    add_section("Study Title: Personalized Immunomodulation in Pediatric Sepsis-Induced MODS (PRECISE)", "")
    add_section("Version Date: June 24, 2024", "")

    add_section("SUMMARY", content.get("summary", ""))
    add_section("BACKGROUND", content.get("background", ""))
    add_section("NUMBER OF PARTICIPANTS", content.get("numberOfParticipants", ""))
    add_section("STUDY PROCEDURES", content.get("studyProcedures", ""))
    add_section("ALTERNATIVE PROCEDURES", content.get("alternativeProcedures", ""))
    add_section("RISKS", content.get("risks", ""))
    add_section("BENEFITS", content.get("benefits", ""))
    add_section("COSTS AND COMPENSATION TO PARTICIPANTS", content.get("costsAndCompensationToParticipants", ""))
    add_section("SINGLE IRB CONTACT", content.get("singleIRBContact", ""))

    # Adding signature fields (static content, as per the provided example)
    story.append(Spacer(1, 20))
    story.append(Paragraph("PARENT/GUARDIAN CONSENT:", section_title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("I confirm that I have read this parental permission document and have had the opportunity to ask questions. I will be given a signed copy of the parental permission form to keep.", normal_text_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Child’s Name: __________________________________________", normal_text_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Parent/Guardian’s Name: __________________________________", normal_text_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Parent/Guardian’s Signature: ______________________________ Date/Time: ____________", normal_text_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Name of Person Obtaining Authorization and Consent: ____________________________", normal_text_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Signature of Person Obtaining Authorization and Consent: ____________ Date/Time: ____________", normal_text_style))

    # Generate PDF
    doc.build(story)

    buffer.seek(0)
    return StreamingResponse(buffer, media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=consent_form.pdf"})


if __name__ == "__main__":
    import uvicorn



    uvicorn.run(app, host="0.0.0.0", port=8000)
