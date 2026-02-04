from langchain_core.tools import tool

# wrap any function as a LangChain tool to be passed to agent
# docstring acts as tool description for agent

@tool
def note_tool(note):
    """
    Saves a note to a local file.

    Args:
        note (str): The note content to be saved.
    
    """
    with open("notes.txt", "a") as f:
        f.write(note + "\n")
    return "Note saved successfully."