from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
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
        token=app_token,
        namespace=keyspace,
        collection_name="github_issues",
        embedding=embeddings
    )

    return vstore

# Connect to AstraDB vector store
vstore = connect_to_vstore()

add_to_vstore = input("Do you want to update the issues? (y/N): ").lower() in ["y", "yes"]

print("Loading...")

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

    # # Example query to retrieve similar issues from the vector store - NOT using agent.
    # search_term = "flash messages"
    # print("\nSearching for issues regarding:", search_term)
    # results = vstore.similarity_search(search_term, k=3) # k is the number of similar documents to retrieve

    # for res in results:
    #     print(f"\n* {res.page_content} \n {res.metadata}\n")

    

# Create a langchain retriever tool to search the vector store
retriever = vstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 3}) # k is the number of similar documents to retrieve

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="github_search",
    description=(
        "Search embedded GitHub issues using semantic similarity. "
        "Use this tool to find relevant issues before answering."
    )
)

# Create the OpenAI chat model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0) #known-stable, agent-friendly model
tools = [retriever_tool]

system_prompt = """

You are a helpful assistant that answers questions about GitHub issues from a specific repository.

You have access to a tool called `github_search` that retrieves relevant GitHub issues using semantic search.
Always use `github_search` to find relevant issues before answering. Base your answers only on the retrieved issues.
Each retrieved document includes metadata fields such as author and created_at. Use them when summarising.
Do not guess or invent information

If no relevant issues are found, say so clearly.

""" # Prompt tells openAI model how to behave and use its provided tools

# Your system prompt should answer four questions for the model:
    # 1. Who am I?
    # 2. What data am I allowed to use?
    # 3. What tool should I rely on?
    # 4. What should I do if info is missing?

# Create the agent
agent = create_agent(
    model=model, 
    tools=tools, 
    system_prompt=system_prompt
) # the create_agent method itself injects chat history, scratchpad, and tool call traces

# Interactive GitHub Issue Q&A loop
while(question := input("\nAsk about GitHub issues (or 'q' to quit): ")) != "q":

    # 'result' is a state object, not just a string. 
    # everything the agent thinks, does, and says ends up in 'messages'
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}) # Pass question to agent
    
    # Stream agent execution step-by-step
    for chunk in agent.stream(result, stream_mode="updates"):
        print("\n--- update ---")
        print(chunk)

    print("\n Final result: " + result["messages"][-1].content) # Print agent's response

    # result["messages"] is the full conversation history of this request 
    # (system prompt, user message, any intermediate reasoning steps, tool calls, tool outputs, final answer)
    # its a list, ordered in time.
    # -1 grabs the last message in the list.

    # .content extracts the text content of that message object