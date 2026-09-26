import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from tools import tools


Path("data").mkdir(exist_ok=True)


DEFAULT_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


GEMINI_MODELS = {
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
}


OPENAI_MODELS = {
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna"
}


ALLOWED_MODELS = GEMINI_MODELS | OPENAI_MODELS


SYSTEM_PROMPT = """
You are a helpful Agentic AI assistant named CustomSDGPT.

You can:
1. Answer normal questions.
2. Use tools when needed.
3. Search uploaded documents using the RAG tool.
4. Search the web for latest/current information using Tavily Search.
5. Remember important user information using the memory tool.
6. Recall memory when useful.
7. Use calculator for math.
8. Use CDC PLACES data for supported community health questions.

Rules:
- If the user asks about latest news, current events, recent updates,
  today's information, current prices, current people, current versions,
  new releases, or anything time-sensitive, use Tavily Search.

- If the user asks about an uploaded document,
  use search_uploaded_documents.

- If the user asks you to remember something,
  use remember_this.

- If the user asks about previous preferences or saved facts,
  use recall_memory.

- Use calculator for math questions.

- Use the CDC community health tool for supported county-level
  public health questions.

- When using web search, summarize clearly and mention that the
  answer is based on web search results.

- Be clear, helpful, and concise.
"""


def normalize_model_name(model_name: str | None) -> str:
    """
    Validate selected model from frontend.
    If model is missing or not allowed, fallback to DEFAULT_MODEL.
    """

    if not model_name:
        return DEFAULT_MODEL

    model_name = model_name.strip()

    if model_name not in ALLOWED_MODELS:
        return DEFAULT_MODEL

    return model_name


def build_agent(model_name: str):
    """
    Build one LangGraph agent using the selected Gemini or OpenAI model.
    """

    selected_model = normalize_model_name(model_name)

    # -------------------------------------------------
    # OpenAI
    # -------------------------------------------------
    if selected_model in OPENAI_MODELS:

        llm = ChatOpenAI(
            model=selected_model,
            streaming=True,

            # Important:
            # GPT-5.6 tool calling should use OpenAI Responses API.
            use_responses_api=True
        )

    # -------------------------------------------------
    # Google Gemini
    # -------------------------------------------------
    else:

        llm = ChatGoogleGenerativeAI(
            model=selected_model,
            temperature=0.3,
            streaming=True
        )

    # Give all CustomSDGPT tools to the selected LLM.
    llm_with_tools = llm.bind_tools(tools)

    # -------------------------------------------------
    # CHATBOT NODE
    # -------------------------------------------------
    def chatbot_node(state: MessagesState):

        messages = [
            SystemMessage(content=SYSTEM_PROMPT)
        ] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    # -------------------------------------------------
    # TOOL NODE
    # -------------------------------------------------
    tool_node = ToolNode(tools)

    # -------------------------------------------------
    # LANGGRAPH WORKFLOW
    # -------------------------------------------------
    workflow = StateGraph(MessagesState)

    workflow.add_node(
        "chatbot",
        chatbot_node
    )

    workflow.add_node(
        "tools",
        tool_node
    )

    # START → chatbot
    workflow.add_edge(
        START,
        "chatbot"
    )

    # chatbot decides:
    # answer directly OR call a tool
    workflow.add_conditional_edges(
        "chatbot",
        tools_condition
    )

    # tool result goes back to chatbot
    workflow.add_edge(
        "tools",
        "chatbot"
    )

    # -------------------------------------------------
    # LANGGRAPH CHECKPOINT MEMORY
    # -------------------------------------------------
    conn = sqlite3.connect(
        "data/langgraph_checkpoints.sqlite",
        check_same_thread=False
    )

    checkpointer = SqliteSaver(conn)

    return workflow.compile(
        checkpointer=checkpointer
    )


_AGENT_CACHE = {}


def get_agent(model_name: str | None = None):
    """
    Return cached LangGraph agent for the selected model.

    If the agent has not been created yet,
    create it once and reuse it.
    """

    selected_model = normalize_model_name(
        model_name
    )

    if selected_model not in _AGENT_CACHE:

        _AGENT_CACHE[selected_model] = build_agent(
            selected_model
        )

    return _AGENT_CACHE[selected_model]