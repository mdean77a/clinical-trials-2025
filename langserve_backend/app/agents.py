from typing import TypedDict, Annotated, Dict, Any, Optional, AsyncGenerator
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessageGraph, add_messages
from langchain_core.runnables import RunnableConfig
from langchain.callbacks import AsyncIteratorCallbackHandler
import asyncio

from .queries import (
    summary_query,
    background_query,
    number_of_participants_query,
    study_procedures_query,
    alt_procedures_query,
    risks_query,
    benefits_query
)

from .rag_builder import RagBuilder

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: Annotated[str, add_messages]
    background: Annotated[str, add_messages]
    number_of_participants: Annotated[str, add_messages]
    study_procedures: Annotated[str, add_messages]
    alt_procedures: Annotated[str, add_messages]
    risks: Annotated[str, add_messages]
    benefits: Annotated[str, add_messages]

class ClinicalTrialGraph:
    def __init__(self, rag_builder: RagBuilder, files: list[str] = []):
        self.rag_chain = rag_builder.rag_chain if len(files) == 0 else rag_builder.get_rag_with_filters(files)
        self.compiled_graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Define nodes for each section
        workflow.add_node("Summarizer", self.summary_node)
        workflow.add_node("Background", self.background_node)
        workflow.add_node("Numbers", self.number_of_participants_node)
        workflow.add_node("Procedures", self.study_procedures_node)
        workflow.add_node("Alternatives", self.alt_procedures_node)
        workflow.add_node("Risks", self.risks_node)
        workflow.add_node("Benefits", self.benefits_node)

        # Connect START to all nodes for parallel execution
        nodes = ["Summarizer", "Background", "Numbers", "Procedures", "Alternatives", "Risks", "Benefits"]
        for node in nodes:
            workflow.add_edge(START, node)
            workflow.add_edge(node, END)

        # Set the entry point
        workflow.set_entry_point("Summarizer")

        return workflow.compile()

    async def streaming_node(self, state: AgentState, field: str, query: str) -> AsyncGenerator[Dict, None]:
        callback = AsyncIteratorCallbackHandler()
        runnable = self.rag_chain.with_config(callbacks=[callback])
        task = asyncio.create_task(runnable.ainvoke({"question": query()}))
        
        current_content = ""
        async for token in callback.aiter():
            current_content += token
            yield {field: [current_content]}
        
        await task

    async def summary_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "summary", summary_query):
            yield update

    async def background_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "background", background_query):
            yield update

    async def number_of_participants_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "number_of_participants", number_of_participants_query):
            yield update

    async def study_procedures_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "study_procedures", study_procedures_query):
            yield update

    async def alt_procedures_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "alt_procedures", alt_procedures_query):
            yield update

    async def risks_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "risks", risks_query):
            yield update

    async def benefits_node(self, state: AgentState) -> AsyncGenerator[Dict, None]:
        async for update in self.streaming_node(state, "benefits", benefits_query):
            yield update

    async def arun(self, config: Optional[RunnableConfig] = None) -> Dict[str, str]:
        final_state = await self.compiled_graph.arun({}, config)
        return {
            "summary": final_state["summary"][0] if final_state["summary"] else "",
            "background": final_state["background"][0] if final_state["background"] else "",
            "number_of_participants": final_state["number_of_participants"][0] if final_state["number_of_participants"] else "",
            "study_procedures": final_state["study_procedures"][0] if final_state["study_procedures"] else "",
            "alt_procedures": final_state["alt_procedures"][0] if final_state["alt_procedures"] else "",
            "risks": final_state["risks"][0] if final_state["risks"] else "",
            "benefits": final_state["benefits"][0] if final_state["benefits"] else ""
        }

    async def astream(self, config: Optional[RunnableConfig] = None):
        targets = {
            "summary": "",
            "background": "",
            "number_of_participants": "",
            "study_procedures": "",
            "alt_procedures": "",
            "risks": "",
            "benefits": ""
        }
        async for update in self.compiled_graph.astream(targets, config, stream_mode="updates"):
            yield update