


# Imports #
### IMPORTS #####
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
from langchain_ollama import ChatOllama

#for HILT
from langgraph.types import Command, interrupt
from langchain_core.messages import SystemMessage
#

#### LOAD API KEYS ####

load_dotenv()

# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")



#### State ##### 
class State(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]

#### Tools #####
arxiv_api = ArxivAPIWrapper(top_k_results=3,doc_content_chars_max=500)
arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_api,description="Search  arxiv  for research paper ")

wiki_api = WikipediaAPIWrapper(top_k_results=2,doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api,description="Search Wikipedia For general Knowledge ")

tavily_tool = TavilySearch(description="Search the Web latest info",search_depth="basic",time_range="month")


# HUMAN APPROVAL Tool (Human-in-the-loop)
@tool
def human_decision(query: str):
    """
    Ask a human expert for guidance when the AI is unsure
    or when the user requests expert advice.
    """
    human_response = interrupt({"query": query})
    return {"messages": [human_response]}

#combined the tool 
tools = [arxiv_tool,wiki_tool,tavily_tool,human_decision]


#### LLM ####
llm = ChatOllama(model="llama3.2:latest",temperature=0.2)

#bind tools to llm
llm_with_tools = llm.bind_tools(tools)


#### Nodes ####

#llm Node

def llm_node(state: State):

    system_prompt = SystemMessage(
        content="""
You are an AI assistant with tools.

If the user asks for:
- expert advice
- guidance
- complex decision making

You MUST call the `human_decision` tool to ask a human expert.
"""
    )

    messages = [system_prompt] + state["messages"]

    response = llm_with_tools.invoke(messages)

    print("DEBUG TOOL CALLS:", response.tool_calls)

    return {"messages": [response]}


tool_node = ToolNode(tools=tools)


#Graph declaration
graph = StateGraph(State)

##FLOW##
graph.add_node("llm", llm_node)
graph.add_node("tools", tool_node)

graph.add_conditional_edges(
    "llm",tools_condition)

graph.add_edge("tools", "llm")
graph.add_edge(START,"llm")

#### Memory ####

memory = MemorySaver()
app = graph.compile(checkpointer=memory)



#### RUN CHATBOT LOOP ####

user_input = "I need Some expert guidence for building AI agent. Could you assist me?"
config = {"configurable": {"thread_id": "rahul_chat"}}

print("\n🤖 Chatbot is running... (type 'exit' to stop)\n")

while True:

    user_input = input("User: ")

    if user_input.lower() == "exit":
        break

    events = app.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values"
    )

    for event in events:

        # Print AI messages
        if "messages" in event:
            event["messages"][-1].pretty_print()

        # Handle Human Interrupt
        if "__interrupt__" in event:

            interrupts = event["__interrupt__"]

            if interrupts:

                interrupt_data = interrupts[0].value

                print("\n⚠️ Human approval required!")
                print("AI Question:", interrupt_data["query"])

                human_input = input("Human: ")

                resume_events = app.stream(
                    Command(resume=human_input),
                    config=config,
                    stream_mode="values"
                )

                for r in resume_events:
                    if "messages" in r:
                        r["messages"][-1].pretty_print()