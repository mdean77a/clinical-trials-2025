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

class AgentState(TypedDict):
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
        inputs = {"messages":[HumanMessage(content="")]}
        state_stream = self.compiled_graph.stream(inputs)
        for state_update in state_stream:
            yield state_update

    async def summary_node(self, state):
        async for response in self.rag_chain.stream(summary_query):
            state["summary"] = response
            yield state

    async def background_node(self, state):
        async for response in self.rag_chain.stream(background_query):
            state["background"] = response
            yield state

    async def number_of_participants_node(self, state):
        async for response in self.rag_chain.stream(number_of_participants_query):
            state["number_of_participants"] = response
            yield state

    async def study_procedures_node(self, state):
        async for response in self.rag_chain.stream(study_procedures_query):
            state["study_procedures"] = response
            yield state

    async def alt_procedures_node(self, state):
        async for response in self.rag_chain.stream(alt_procedures_query):
            state["alt_procedures"] = response
            yield state

    async def risks_node(self, state):
        async for response in self.rag_chain.stream(risks_query):
            state["risks"] = response
            yield state

    async def benefits_node(self, state):
        async for response in self.rag_chain.stream(benefits_query):
            state["benefits"] = response
            yield state
