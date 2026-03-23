"""
🚀 LangGraph Final Chatbot (Production Ready)
Features:
- Memory
- Multi-tool (Arxiv, Wikipedia, Tavily, Weather)
- Multi-step reasoning
- Proper streaming (ChatGPT-like)
"""


##### Streaming #####

#### IMPORTS #####
import os
import requests
from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Tools
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_tavily import TavilySearch
from langchain.tools import tool

# LLM
from langchain_groq import ChatGroq


#### LOAD API KEYS ####
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "false"

#### STATE #####
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


#### TOOLS #####

# Arxiv Tool
arxiv_tool = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500),
    description="Search Arxiv for research papers"
)

# Wikipedia Tool
wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500),
    description="Search Wikipedia for general knowledge"
)

# Tavily Tool
tavily_tool = TavilySearch(
    description="Search the web for latest information"
)

# Weather Tool
@tool
def get_weather(city: str) -> str:
    """Get current weather of a city"""
    return requests.get(f"https://wttr.in/{city}?format=3").text


# Combine all tools
tools = [arxiv_tool, wiki_tool, tavily_tool, get_weather]


#### LLM #####

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0.2,
    streaming=True   # Enable streaming at the model level (IMPORTANT for real streaming)
)

llm_with_tools = llm.bind_tools(tools)


#### NODES #####

# LLM Node
def llm_node(state: State):
    response = llm_with_tools.invoke(
        [{"role": "system", "content": "You are a smart AI assistant."}]
        + state["messages"]
    )
    return {"messages": [response]}

# Tool Node
tool_node = ToolNode(tools)


#### GRAPH #####

graph = StateGraph(State)

graph.add_node("llm", llm_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "llm")

graph.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

graph.add_edge("tools", "llm")


#### MEMORY #####

memory = MemorySaver()
app = graph.compile(checkpointer=memory)


#### CHAT LOOP #####

config = {"configurable": {"thread_id": "rahul_chat1"}}

print("\n🤖 Chatbot is running... (type 'exit' to stop)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye 👋")
        break

    print("Bot: ", end="", flush=True)

    last_output = ""

    for event in app.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values"   
    ):
        print("\n[DEBUG] New event received")  # 👈 add this
        message = event["messages"][-1]

        if message.type == "ai":
            new_text = message.content

            # Print only new part (real streaming)
            print(new_text[len(last_output):], end="", flush=True)
            last_output = new_text

    print("\n")