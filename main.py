from langgraph.graph import StateGraph, END
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List

load_dotenv()
_repl = PythonREPL()

SYSTEM_PROMPT = """
You are an assistant that writes **only** executable Python code, with no extra text or commentary.
Use the `diagrams` package (https://diagrams.mingrammer.com/) to produce an
architecture diagram. The code **must** save the diagram to a file called
`architecture_diagram.png` in the working directory.

**Constraints**

1. Return only valid Python source code.
2. Do **not** wrap the code in markdown fences.
"""

@tool(description="Execute Python code using a REPL and return the output or any error.")
def python_repl(code: str) -> str:
    try:
        return _repl.run(code)
    except BaseException as e:
        return f"❌ {e.__class__.__name__}: {e}"


# === Memory structure for the graph ===
class ChatState(BaseModel):
    user_input: str
    history: List[str] = []
    feedback: str = ""

# === Nodes ===

def generate_response(state: ChatState) -> ChatState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(state.history[-1] + state.feedback) if state.feedback!="" else state.user_input),
    ]
    python_code = llm(messages).content.strip()
    state.history.append(python_code)
    return state

def execute_code(state: ChatState) -> ChatState:
    last_code = state.history[-1]
    output = python_repl(last_code)
    print("✅ Diagram generated. Check `architecture_diagram.png`.")
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

# === LangGraph Builder ===
builder = StateGraph(ChatState)

builder.add_node("generate_response", generate_response)
builder.add_node("execute_code", execute_code)
builder.add_node("get_feedback", get_feedback)

builder.set_entry_point("generate_response")
builder.add_edge("generate_response", "execute_code")
builder.add_edge("execute_code", "get_feedback")
builder.add_conditional_edges("get_feedback", feedback_router)

graph = builder.compile()


ui="""Generate a diagram of a simple web application architecture with the following components:
- A web server
- A database
- A load balancer
- A cache
The web server should be connected to the load balancer, which is connected to the database and cache.
The diagram should be saved to a file called `architecture_diagram.png` in the working directory.
Use EC2 instances for the web server and database, and an S3 bucket for the cache.
The diagram should be in PNG format.
"""

state = ChatState(user_input=ui)

state = graph.invoke(state)

print(state)

