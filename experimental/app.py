import langchain_community
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import getVectorstore 
from getVectorstore import getVectorstore
from qdrant_client.http import models as rest
from dotenv import load_dotenv
import os, getpass, time
import prompts
from prompts import rag_prompt_template
from langchain.prompts import ChatPromptTemplate
from defaults import default_llm
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from datetime import date
import queries
from queries import summary_query
from queries import background_query
from queries import number_of_participants_query
from queries import study_procedures_query
from queries import alt_procedures_query
from queries import risks_query
from queries import benefits_query
import makeMarkdown
from makeMarkdown import makeMarkdown
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from langchain_core.messages import HumanMessage

# Usual method to get the key
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Backup method in case above did not work
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# Load the document - here we are just using a protocol in a specific directory
# In the demo project this will come from Jeeva's code
print(f"Current working directory: {os.getcwd()}")
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change the current working directory to the script's directory
os.chdir(script_dir)
print(f"Current working directory: {os.getcwd()}")
file_path = './documents/protocol.pdf'
print(f"Attempting to access file: {os.path.abspath(file_path)}")

if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist. Please check the path and file name.")

separate_pages = []             
loader = PyMuPDFLoader(file_path)
page = loader.load()
separate_pages.extend(page)
print(f"Number of separate pages: {len(separate_pages)}")

# OyMuPDFLoader loads pages into separate docs!
# This is a problem when we chunk because we only chunk individual
# documents.  We need ONE overall document so that the chunks can
# overlap between actual PDF pages.
document_string = ""
for page in separate_pages:
    document_string += page.page_content
print(f"Length of the document string: {len(document_string)}")

# CHOP IT UP
def tiktoken_len(text):
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(
        text,
    )
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap = 200,
    length_function = tiktoken_len
)
text_chunks = text_splitter.split_text(document_string)
print(f"Number of chunks: {len(text_chunks)} ")
document = [Document(page_content=chunk) for chunk in text_chunks]
print(f"Length of  document: {len(document)}")

qdrant_vectorstore = getVectorstore(document, file_path)

# Helper function that lets me create a retriever for a specific document
"""
This code sets up the search type but more importantly it has the filter
set up correctly.  We get a list of document titles that we want to include
in the filter, and pass it into the function, returning the retriever.

"""

def create_protocol_retriever(document_titles):
    return qdrant_vectorstore.as_retriever(
        search_kwargs={
            'filter': rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="metadata.document_title",
                        match=rest.MatchAny(any=document_titles)
                    )
                ]
            ),
            'k': 15,                                       
        }
    )

# Usage example
# document_titles = ["consent.pdf", "protocol.pdf"]
document_titles = ["protocol.pdf"]
protocol_retriever = create_protocol_retriever(document_titles)

# Create prompt
rag_prompt = ChatPromptTemplate.from_template(prompts.rag_prompt_template)

llm = default_llm

rag_chain = (
    {"context": itemgetter("question") | protocol_retriever, "question": itemgetter("question")}
    | rag_prompt | llm | StrOutputParser()
)

# Heading for top of ICF document
protocol_title = rag_chain.invoke({"question": "What is the exact title of this protocol?  Only return the title itself without any other description."})
principal_investigator = rag_chain.invoke({"question":"What is the name of the principal investigator of the study?  Only return the name itself without any other description."})
support = rag_chain.invoke({"question":"What agency is funding the study?  Only return the name of the agency without any other description."})
version_date = date.today().strftime("%B %d, %Y")

heading = f""" 
## Parental Permission, Teen Assent and Authorization Document

**Study Title:** {protocol_title}

**Principal Investigator:** {principal_investigator}

**Version Date:** {version_date}

**Source of Support:** {support}

---

<div style="text-align: center;">

## Part 1 of 2: MASTER CONSENT
</div>

**Parents/Guardians:**
You have the option of having your child or teen join a research study.
This is a parental permission form. It provides a summary of the information the research team
will discuss with you. If you decide that your child can take part in this study, you would sign
this form to confirm your decision. If you sign this form, you will receive a signed copy for your
records. *The word “you” in this form refers to your child/teen unless otherwise indicated.*

**Assent Teen Participants:**
This form also serves as an assent form. That means that if you
choose to take part in this research study, you would sign this form to confirm your choice. Your
parent or guardian would also need to give their permission and sign this form for you to join the
study

**Consent for Continued Participation (Participants who turn 18 during the study):**
This is a consent form for continued participation. It provides a summary of the information the
research team will discuss with you. If you decide that you would like to continue participating in
this research study, you would sign this form to confirm your decision. If you sign this form, you
will receive a signed copy of this form for your records.

---

""" 

# Boilerplate that goes after the generated portions of ICF
boilerplate = """ 
## Right of the Investigator to Withdraw Participants
The investigator can withdraw you from the study without your approval.  If at any time the
investigator believes participating in the study is not the best choice of care, the study
may be stopped and other care prescribed.  If unexpected medical problems come up, the investigator
may decide to stop your participation in the study.

---
## New Information
Sometimes during the course of a research project, new information becomes available about the
drugs that are being studied. If this happens, your research doctor will tell you about it and discuss
with you whether you want to continue in the study. If you decide to continue in the study, you
may be asked to sign an updated consent form. Also, on receiving new information the research
doctor might consider it to be in your best interests to withdraw you from the study. He/she will
explain the reasons and arrange for your medical care to continue.

---

## Costs and Compensation to Participants
While you are in this study, the cost of your usual medical care - procedures, medications and
doctor visits - will continue to be billed to you or your insurance. There will be no additional costs
to you for your participation in this study. You will receive up to \$50 to compensate you for your
time when completing the follow-up surveys at the 3- and 12-month time points. You will receive
\$25 for each follow-up period once we receive your answers to the surveys. Any tests that are
performed or medications administered solely for the purposes of being in this study will be paid
for by the research doctor. The National Institutes of Health is providing funding for this study.

---

## Single IRB Contact
**Institutional Review Board:** The University of Utah Institutional Review Board (IRB) is
serving as the single IRB (SIRB) for this study. Contact the SIRB if you have questions, complaints
or concerns which you do not feel you can discuss with the investigator. The University of Utah
IRB may be reached by phone at (801) 581-3655 or 
by e-mail at irb@hsc.utah.edu.

"""

# Heading for Part 2 of the ICF document, which is the local context part
part2 = f""" 
## Parental Permission, Teen Assent and Authorization Document

**Study Title:** {protocol_title}

**Principal Investigator:** {principal_investigator}

**Source of Support:** {support}

---

<div style="text-align: center;">

## Part 2 of 2: SITE SPECIFIC INFORMATION
</div>

This section of the consent form, as well as signature pages, are very specific
to individual sites, and the Clinical Trial Accelerator does not have the ability
to create this section.principal_investigator

---

"""

# Create AgentState object and include all the pieces in separate fields
# Not sure if add_messages is necessary because I don't have any overwrites later (YET)
# But future enhancement might include a subnetwork that edits each piece further
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]     # not sure I need this
    summary: Annotated[str, add_messages]
    background: Annotated[str, add_messages]
    number_of_participants: Annotated[str, add_messages]
    study_procedures: Annotated[str, add_messages]
    alt_procedures: Annotated[str, add_messages]
    risks: Annotated[str, add_messages]
    benefits: Annotated[str, add_messages]

   # Set up all the node definitions - each simply returns its query
def summary_node(state):
    summary = rag_chain.invoke({"question":summary_query()})
    return {"summary":[summary]}

def background_node(state):
    background = rag_chain.invoke({"question":background_query()})
    return {"background":[background]}

def number_of_participants_node(state):
    number_of_participants = rag_chain.invoke({"question":number_of_participants_query()})
    return {"number_of_participants": [number_of_participants]}

def study_procedures_node(state):
    study_procedures = rag_chain.invoke({"question":study_procedures_query()})
    return {"study_procedures": [study_procedures]}

def alt_procedures_node(state):
    alt_procedures = rag_chain.invoke({"question":alt_procedures_query()})
    return {"alt_procedures": [alt_procedures]}

def risks_node(state):
    risks = rag_chain.invoke({"question":risks_query()})
    return {"risks": [risks]}

def benefits_node(state):
    benefits = rag_chain.invoke({"question":benefits_query()})
    return {"benefits": [benefits]}

 # Now construct the graph.  My first attempt simply linked them in
# sequence to mimic the brute force method done earlier.  But this
# graph runs the agents in parallel.

uncompiled_graph = StateGraph(AgentState)

# Add nodes
uncompiled_graph.add_node("Summarizer", summary_node)
uncompiled_graph.add_node("Background", background_node)
uncompiled_graph.add_node("Numbers", number_of_participants_node)
uncompiled_graph.add_node("Procedures", study_procedures_node)
uncompiled_graph.add_node("Alternatives", alt_procedures_node)
uncompiled_graph.add_node("Risks", risks_node)
uncompiled_graph.add_node("Benefits", benefits_node)

# Edges from the START
uncompiled_graph.add_edge(START,"Summarizer")
uncompiled_graph.add_edge(START,"Background")
uncompiled_graph.add_edge(START,"Numbers")
uncompiled_graph.add_edge(START,"Procedures")
uncompiled_graph.add_edge(START,"Alternatives")
uncompiled_graph.add_edge(START,"Risks")
uncompiled_graph.add_edge(START,"Benefits")

# Edges to the END
uncompiled_graph.add_edge("Summarizer",END)
uncompiled_graph.add_edge("Background",END)
uncompiled_graph.add_edge("Numbers",END)
uncompiled_graph.add_edge("Procedures",END)
uncompiled_graph.add_edge("Alternatives",END)
uncompiled_graph.add_edge("Risks",END)
uncompiled_graph.add_edge("Benefits",END)

compiled_graph = uncompiled_graph.compile()

start_time = time.time()
inputs = {"messages":[HumanMessage(content="")]}
result = compiled_graph.invoke(inputs)
end_time = time.time()
execution_time = end_time - start_time
print(f"Agent based (parallel) execution time: {execution_time:.2f} seconds.")

pieces_of_consent = [
    heading,
    result['summary'][-1].content,
    result['background'][-1].content,
    result['number_of_participants'][-1].content,
    result['study_procedures'][-1].content,
    result['alt_procedures'][-1].content,
    result['risks'][-1].content,
    result['benefits'][-1].content,
    boilerplate,
    part2
]
ICF_title = "APP Agent Written ICF"
makeMarkdown(pieces_of_consent, ICF_title)
print("Done")
