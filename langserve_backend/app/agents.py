from typing import TypedDict, Annotated, Dict, Any
import json
import asyncio
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

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
    def __init__(self, rag_builder: RagBuilder):
        self.rag_chain = rag_builder.rag_chain
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

        # Edges to the END
        uncompiled_graph.add_edge("Summarizer", END)
        uncompiled_graph.add_edge("Background", END)
        uncompiled_graph.add_edge("Numbers", END)
        uncompiled_graph.add_edge("Procedures", END)
        uncompiled_graph.add_edge("Alternatives", END)
        uncompiled_graph.add_edge("Risks", END)
        uncompiled_graph.add_edge("Benefits", END)

        return uncompiled_graph.compile()

    async def summary_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        summary = self.rag_chain.invoke({"question": summary_query()})
        state["summary"] = summary
        return state

    async def background_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        background = self.rag_chain.invoke({"question": background_query()})
        state["background"] = background
        return state

    async def number_of_participants_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        number_of_participants = self.rag_chain.invoke({"question": number_of_participants_query()})
        state["number_of_participants"] = number_of_participants
        return state

    async def study_procedures_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        study_procedures = self.rag_chain.invoke({"question": study_procedures_query()})
        state["study_procedures"] = study_procedures
        return state

    async def alt_procedures_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        alt_procedures = self.rag_chain.invoke({"question": alt_procedures_query()})
        state["alt_procedures"] = alt_procedures
        return state

    async def risks_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risks = self.rag_chain.invoke({"question": risks_query()})
        state["risks"] = risks
        return state

    async def benefits_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        benefits = self.rag_chain.invoke({"question": benefits_query()})
        state["benefits"] = benefits
        return state

    async def run(self):
        initial_state = {}
        state_stream = self.compiled_graph.stream(initial_state)
        try:
            async for state_update in state_stream.__aiter__():
                yield json.dumps(state_update, indent=2)
        finally:
            await state_stream.aclose()

# Example usage
# rag_builder = RagBuilder()  # Assuming RagBuilder is already defined
# agent = ClinicalTrialAgent(rag_builder)
# async for state in agent.run():
#     print(state)
