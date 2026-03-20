
##########################################################################################################################################
#@ langgraph chatbot full script
"""
# 🚀 LangGraph Building Series
# 2nd step
# Simple chatbot using Groq LLM and tools from langchain_community. 
# This chatbot can query Arxiv, Wikipedia, and perform web searches using Tavily. We will learn how to integrate multiple tools with a Groq LLM to create a powerful chatbot that can access a wide range of information.
# """

import os 
from dotenv import load_dotenv


# @Load API keys
load_dotenv()


os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# @ Import tools
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq

# from langchain.agents import initialize_agent, AgentType

# @ Setup Arxiv Tool
api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
arxiv_tool = ArxivQueryRun(
    api_wrapper=api_wrapper_arxiv,
    description="A tool to query arxiv papers"
)

# @ Setup Wikipedia Tool

api_wrapper_wikipedia = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
wikipedia_tool = WikipediaQueryRun(
    api_wrapper=api_wrapper_wikipedia,
    description="A tool to query wikipedia"
)

# @Setup Tavily Web Search Tool
tavily_tool = TavilySearch(
    description="A tool to search the web using Tavily"
)


#@ Combine tools into a list
tools = [arxiv_tool, wikipedia_tool, tavily_tool]


# @Initialize Groq LLM
llm = ChatGroq(
    model="qwen/qwen3-32b",  # or your available Groq model
    temperature=0.7
)

##LLM WITh TOOLS 
llm_with_tools = llm.bind_tools(tools=tools)

print("LLM with tools ready to use!")
invoke = llm_with_tools.invoke("What are the recent news on AI?")
print(invoke)



#######################################################################################################################
# """ 
# # 🚀 LangGraph Building Series
# # 1. THIS IS the first program in the series, where we will learn how to use the Arxiv and Wikipedia API Wrappers from the langchain_community library. These wrappers allow us to easily query information from Arxiv and Wikipedia, which can be very useful for building chatbots and other applications that require access to a large amount of information.
# # 1st step 
# """
# import os
# from dotenv import load_dotenv
# load_dotenv()

# #tools
# from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
# from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper

# #! Arxiv API Wrapper
# api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=2,doc_content_chars_max=500)
# arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv,description="A tool to query arxiv papers")

# print(arxiv.name)

# arxiv_result = arxiv.invoke("What are the latest papers on graph neural networks?")
# print(arxiv_result)

# #! Wikipedia API Wrapper
# api_wrapper_wikipedia = WikipediaAPIWrapper(top_k_results=2,doc_content_chars_max=500)
# wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper_wikipedia,description="A tool to query wikipedia")

# print(wikipedia.name)

# wikipedia_result = wikipedia.run("capital Of India?")
# print(wikipedia_result)
