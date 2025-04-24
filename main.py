from langgraph.graph import StateGraph, END
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from typing import List
import os

load_dotenv()
_repl = PythonREPL()

# System prompt to instruct the model
SYSTEM_PROMPT = """
You are an assistant that writes **only** executable Python code, with no extra text or commentary.
Use the `diagrams` package (https://diagrams.mingrammer.com/) to produce an
architecture diagram. The code **must** save the diagram to a file at:
`generated_diagrams/architecture_diagram.png`

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

def generate_response(state: ChatState) -> ChatState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(state.history[-1] + state.feedback) if state.feedback!="" else state.user_input),
    ]
    python_code = llm(messages).content.strip()
    #print("Generated Code:\n", python_code)
    state.history.append(python_code)
    return state

def execute_code(state: ChatState) -> ChatState:
    #print("Executing Code:\n", state.history[-1])
    reply = python_repl(state.history[-1])
    return state
def get_feedback(state: ChatState) -> ChatState:
    feedback = input("Would you like to modify the diagram? If yes, describe the change. If it's okay, type 'ok':\n")
    state.feedback = feedback.lower().strip()
    return state

# === Conditional router ===
def feedback_router(state: ChatState) -> str:
    if state.feedback == "ok":
        return END
    else:
        state.user_input = state.feedback
        return "generate_response"

builder = StateGraph(ChatState)
builder.add_node("generate_response", generate_response)
builder.add_node("execute_code", execute_code)
builder.add_node("get_feedback", get_feedback)
builder.set_entry_point("generate_response")
builder.add_edge("generate_response", "execute_code")
builder.add_edge("execute_code", "get_feedback")
builder.add_conditional_edges("get_feedback", feedback_router)
graph = builder.compile()

def generate_and_save_diagram(user_prompt: str) -> str:
    print(user_prompt)
    os.makedirs("generated_diagrams", exist_ok=True)
    state = ChatState(user_input=user_prompt, history=[])
    graph.invoke(state)
    diagram_path = "generated_diagrams/architecture_diagram.png"
    return diagram_path if os.path.exists(diagram_path) else None

 