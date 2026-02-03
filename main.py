from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain.tools import create_retriever_tool
from langchainhub import hub
from github_loader import fetch_github_issues

load_dotenv()

def connect_to_vstore():
    """Connect to AstraDB vector store."""

    # Load AstraDB credentials from environment variables
    api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    app_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

    if os.getenv("ASTRA_DB_KEYSPACE"):
        keyspace = os.getenv("ASTRA_DB_KEYSPACE")
    else:
        keyspace = None

    # Convert git issues and user queries to vectors
    embeddings = OpenAIEmbeddings()

    # Initialize AstraDB vector store
    vstore = AstraDBVectorStore(
        api_endpoint=api_endpoint,
        app_token=app_token,
        keyspace=keyspace,
        collection_name="github_issues",
        embedding=embeddings
    )

    return vstore

# Connect to AstraDB vector store
vstore = connect_to_vstore()

add_to_vstore = input("Do you want to update the issues? (y/N): ").lower() in ["y", "yes"]

if add_to_vstore:
    # Fetch git issues from an example repository
    issues = fetch_github_issues("techwithtim", "Flask-Web-App-Tutorial")

    # Clear existing collection before adding new documents
    try:
        vstore.delete_collection()
    except:
        pass

    # Connect again and add fetched issues to the vector store
    vstore = connect_to_vstore()
    vstore.add_documents(issues)

    results = vstore.similarity_search("flash messages", k=3) # k is the number of similar documents to retrieve
    
    for res in results:
        print(f"* {res.page_content} {res.metadata}")
