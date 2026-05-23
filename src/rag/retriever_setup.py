"""
Retriever setup and vector store configuration.
"""

import os

from langchain_core.documents import Document
from langchain_core.tools import create_retriever_tool
# from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import FAISS

from src.core.config import settings

# embeddings = OpenAIEmbeddings()
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# Global variable to store the FAISS vectorstore instance
# This ensures get_retriever() can access documents stored by retriever_chain()
_faiss_vectorstore = None


def retriever_chain(chunks: list[Document]):
    """
    Initialize and store documents in FAISS vector database.

    Args:
        chunks: List of document chunks to store.

    Returns:
        Boolean indicating success of the operation.
    """
    global _faiss_vectorstore

    try:
        # Commenting out Qdrant code for temporary FAISS usage
        # vectorstore = QdrantVectorStore.from_documents(
        #     documents=chunks,
        #     embedding=embeddings,
        #     url=settings.QDRANT_URL,
        #     api_key=settings.QDRANT_API_KEY,
        #     collection_name=settings.CODE_COLLECTION,
        # )
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )

        # Store the vectorstore globally so get_retriever() can access it
        _faiss_vectorstore = vectorstore

        print("FAISS vector store initialized with documents")
        print(f"Vectorstore contains {len(chunks)} document chunks")
        return True
    except Exception as e:
        print(f"Error storing documents in FAISS: {e}")
        return False


from langchain_core.tools import create_retriever_tool

def get_retriever():
    global _faiss_vectorstore

    try:
        if _faiss_vectorstore is None:
            raise ValueError("No documents uploaded yet.")

        retriever = _faiss_vectorstore.as_retriever(
            search_kwargs={"k": 3}
        )

        print("Using existing FAISS vectorstore with uploaded documents")

        # Load description
        if os.path.exists("description.txt"):
            with open("description.txt", "r", encoding="utf-8") as f:
                description = f.read()
        else:
            description = "uploaded documents"

        retriever_tool = create_retriever_tool(
            retriever,
            "retriever_customer_uploaded_documents",
            f"""
Use this tool ONLY for questions related to:
{description}

If relevant information is found in documents,
answer using the retrieved content.
"""
        )

        return retriever_tool

    except Exception as e:
        print(f"Error initializing retriever: {e}")
        raise e