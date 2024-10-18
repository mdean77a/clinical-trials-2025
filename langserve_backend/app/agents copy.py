from typing import TypedDict, Annotated, Dict, Any
import json
import asyncio
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage

from .queries import summary_query
from .queries import background_query
from .queries import number_of_participants_query
from .queries import study_procedures_query
from .queries import alt_procedures_query
from .queries import risks_query
from .queries import benefits_query

from .rag_builder import RagBuilder

class Consent:
    def __init__(self):
        self.summary = ""
        self.background = ""
        self.number_of_participants = ""
        self.study_procedures = ""
        self.alt_procedures = ""
        self.risks = ""
        self.benefits = ""

class AgentState(TypedDict):
    # consent: Annotated[Consent, add_messages]
    summary: Annotated[str, add_messages]
    background: Annotated[str, add_messages]
    number_of_participants: Annotated[str, add_messages]
    study_procedures: Annotated[str, add_messages]
    alt_procedures: Annotated[str, add_messages]
    risks: Annotated[str, add_messages]
    benefits: Annotated[str, add_messages]

class ClinicalTrialAgent:
    def __init__(self, rag_builder: RagBuilder, files: list[str] = []):
        self.rag_chain = rag_builder.rag_chain  if len(files) == 0 else rag_builder.get_rag_with_filters(files)
        self.compiled_graph = self._build_graph()

    def _build_graph(self):
        uncompiled_graph = StateGraph(AgentState)

        # Add nodes
        uncompiled_graph.add_node("Summarizer", self.summary_node)
        uncompiled_graph.add_node("Background", self.background_node)
        uncompiled_graph.add_node("Numbers", self.number_of_participants_node)
        uncompiled_graph.add_node("Procedures", self.study_procedures_node)
        uncompiled_graph.add_node("Alternatives", self.alt_procedures_node)
        uncompiled_graph.add_node("Risks", self.risks_node)
        uncompiled_graph.add_node("Benefits", self.benefits_node)

        # Edges from the START
        uncompiled_graph.add_edge(START, "Summarizer")
        uncompiled_graph.add_edge(START, "Background")
        uncompiled_graph.add_edge(START, "Numbers")
        uncompiled_graph.add_edge(START, "Procedures")
        uncompiled_graph.add_edge(START, "Alternatives")
        uncompiled_graph.add_edge(START, "Risks")
        uncompiled_graph.add_edge(START, "Benefits")

        # Edge to END
        uncompiled_graph.add_edge("Summarizer", END)

        compiled_graph = uncompiled_graph.compile()
        return compiled_graph

    async def run(self):
        initial_state = {"consent": Consent()}
        state_stream = self.compiled_graph.stream(initial_state,stream_mode="consent")
        for state_update in state_stream:
            print(state_update)
            return state_update

    async def summary_node(self, state):
        async for response in self.rag_chain.stream(summary_query):
            if response:
                print(response)
                summary = state.consent["summary"] + response
                return {"summary": summary}
            else:
                print("No response received for summary")

    async def background_node(self, state):
        async for response in self.rag_chain.stream(background_query):
            if response:
                print(response)
                background = state.consent["background"] + response
                return {"background":background}
            else:
                print("No response received for background")

    async def number_of_participants_node(self, state):
        async for response in self.rag_chain.stream(number_of_participants_query):
            if response:
                print(response)
                number_of_participants = state.consent["number_of_participants"] + response
                return {"number_of_participants": number_of_participants}
            else:
                print("No response received for number of participants")

    async def study_procedures_node(self, state):
        async for response in self.rag_chain.stream(study_procedures_query):
            if response:
                print(response)
                study_procedures = state.consent["study_procedures"] + response
                return {"study_procedures": study_procedures}
            else:
                print("No response received for study procedures")

    async def alt_procedures_node(self, state):
        async for response in self.rag_chain.stream(alt_procedures_query):
            if response:
                print(response)
                alt_procedures = state.consent["alt_procedures"] + response
                return {"alt_procedures": alt_procedures}
            else:
                print("No response received for alternative procedures")

    async def risks_node(self, state):
        async for response in self.rag_chain.stream(risks_query):
            if response:
                print(response)
                risks = state.consent["risks"] + response
                return {"risks": risks}
            else:
                print("No response received for risks")

    async def benefits_node(self, state):
        async for response in self.rag_chain.stream(benefits_query):
            if response:
                print(response)
                benefits = state.consent["benefits"] + response
                return {"benefits": benefits}
            else:
                print("No response received for benefits")
