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
        data = response.json()
    else:
        print("Error:", response.status_code, response.text)
        return []

    print(data)
    return data

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
        # Extract relevant metadata and content into a dictionary
        metadata = {
            "author": entry["user"]["login"],
            "comments": entry["comments"],
            "body": entry["body"],
            "labels": entry["labels"],
            "created_at": entry["created_at"],
        }

        data = entry["title"]

        # Append body if it exists
        if entry["body"]:
            data += entry["body"]

        # Create Document object and append to docs list
        doc = Document(page_content=data, metadata=metadata)
        docs.append(doc)
    
    return docs

# Call function to fetch git issues from an example repository
fetch_github("techwithtim", "Flask-Web-App-Tutorial", "issues")