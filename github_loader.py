import os
import requests
from dotenv import load_dotenv
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()

# Retrieve GitHub token from .env file
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Function to fetch data from GitHub API
def fetch_github(owner, repo, endpoint):
    """Fetch data from a GitHub repository using the GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200: # 200 OK
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return []

# Function to fetch the git issues
def fetch_github_issues(owner, repo):
    issues = fetch_github(owner, repo, "issues")
    return load_issues(issues)

# Function to load git issues into document format
def load_issues(issues):

    # List to hold Document objects
    docs = []

    # Iterate through each issue entry
    for entry in issues:

        title = entry.get("title", "").strip()
        body = entry.get("body") or ""

        author = entry.get("user", {}).get("login", "unknown")
        created_at = entry.get("created_at", "unknown")

        labels = [label.get("name") for label in entry.get("labels", [])]

        # Build page content (what gets embedded & shown to the model)
        page_content = f"""

Title: {title}
Author: {author}
Created at: {created_at}

{body}
""".strip()

        # Extract relevant metadata and content into a dictionary
        metadata = {
            "author": author,
            "created_at":created_at,
            "labels": labels,
            "comments": entry.get("comments", 0)
        }

        # Create LangChain Document object and append to docs list
        doc = Document(page_content=page_content, metadata=metadata)
        docs.append(doc)
    
    return docs