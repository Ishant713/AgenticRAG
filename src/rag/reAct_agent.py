"""
ReAct agent setup for document retrieval and question answering.
"""

import os
import logging

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from src.config.settings import Config
from src.llms.openai import llm
from src.rag.retriever_setup import get_retriever

config = Config()

# Create ReAct agent prompt
template = """
Answer the following questions as best you can.

You have access to the following tools:

{tools}

Tool names:
{tool_names}

Use the following format:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final answer to the original question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template)

class DynamicAgentExecutor:
    """Wrapper that constructs the agent and tools dynamically to ensure the latest retriever is used."""
    
    def invoke(self, input_data, *args, **kwargs):
        try:
            current_tools = [get_retriever()]
        except Exception as e:
            logging.getLogger(__name__).warning(f"Retriever not initialized dynamically: {e}")
            current_tools = []

        if not current_tools:
            return {
                "output": "No documents have been uploaded yet. Please upload a document first.",
                "intermediate_steps": []
            }

        current_react_agent = create_react_agent(llm, current_tools, prompt)
        executor = AgentExecutor(
            agent=current_react_agent,
            tools=current_tools,
            handle_parsing_errors=True,
            max_iterations=2,
            verbose=True,
            return_intermediate_steps=True
        )
        return executor.invoke(input_data, *args, **kwargs)

agent_executor = DynamicAgentExecutor()
