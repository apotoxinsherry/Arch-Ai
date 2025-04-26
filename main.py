from langgraph.graph import StateGraph, END
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from typing import List, Optional
import os

load_dotenv()
_repl = PythonREPL()

# System prompt to instruct the model
SYSTEM_PROMPT = """
You are an assistant that writes **only** executable Python code, with no extra text or commentary.
Use the `diagrams` package (https://diagrams.mingrammer.com/) to produce an architecture diagram.
The code **must** save the diagram to a file at: `generated_diagrams/architecture_diagram.png`

**Constraints**
1. Return only valid Python source code.
2. Do **not** wrap the code in markdown fences.
"""

@tool
def python_repl(code: str) -> str:
    """
    Executes the provided Python code and returns the result.
    Useful for running Python logic or generating diagrams.
    """
    try:
        return _repl.run(code)
    except BaseException as e:
        return f"❌ {e.__class__.__name__}: {e}"

class ChatState(BaseModel):
    user_input: str
    history: List[str] = []
    feedback: str = ""
    iteration: int = 0

def generate_response(state: ChatState) -> ChatState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Adjust prompt based on whether this is initial generation or feedback-based update
    if state.iteration == 0:
        prompt_content = state.user_input
    else:
        prompt_content = f"Original request: {state.user_input}\nFeedback: {state.feedback}\nUpdate the diagram accordingly."
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt_content),
    ]
    
    python_code = llm(messages).content.strip()
    print(python_code)
    state.history.append(python_code)
    return state

def execute_code(state: ChatState) -> ChatState:
    # Execute the code directly without modifying it
    result = python_repl(state.history[-1])
    return state

# Define a separate graph for initial diagram generation and updates
def create_graph():
    builder = StateGraph(ChatState)
    builder.add_node("generate_response", generate_response)
    builder.add_node("execute_code", execute_code)
    builder.set_entry_point("generate_response")
    builder.add_edge("generate_response", "execute_code")
    builder.add_edge("execute_code", END)
    return builder.compile()

def generate_and_save_diagram(user_prompt: str) -> Optional[str]:
    """Generate a diagram based on the user's initial prompt."""
    os.makedirs("generated_diagrams", exist_ok=True)
    graph = create_graph()
    state = ChatState(user_input=user_prompt, iteration=0)
    graph.invoke(state)
    
    diagram_path = "generated_diagrams/architecture_diagram.png"
    return diagram_path if os.path.exists(diagram_path) else None

def update_diagram_with_feedback(original_prompt: str, feedback: str) -> Optional[str]:
    """Update an existing diagram based on user feedback."""
    os.makedirs("generated_diagrams", exist_ok=True)
    
    # Use a constant path for all iterations
    output_path = "generated_diagrams/architecture_diagram.png"

    # Create the graph and execute it to generate the updated diagram
    graph = create_graph()
    state = ChatState(
        user_input=original_prompt,
        feedback=feedback,
        iteration=1  # The iteration number doesn't matter much now
    )

    # Run the graph to generate and execute code (will overwrite the existing file)
    final_state = graph.invoke(state)

    # Check if the file was created
    if os.path.exists(output_path):
        return output_path
    else:
        return None