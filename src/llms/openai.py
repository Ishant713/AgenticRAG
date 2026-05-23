"""
Groq LLM initialization and configuration.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0
)
# import os

# # from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI

# load_dotenv()
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# llm = ChatOpenAI(model="gpt-4o")