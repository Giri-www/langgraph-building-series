

#######################################################################################################################
""" 
# 🚀 LangGraph Building Series
# 1. THIS IS the first program in the series, where we will learn how to use the Arxiv and Wikipedia API Wrappers from the langchain_community library. These wrappers allow us to easily query information from Arxiv and Wikipedia, which can be very useful for building chatbots and other applications that require access to a large amount of information.
# """
import os
from dotenv import load_dotenv
load_dotenv()

#tools
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper

#! Arxiv API Wrapper
api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=2,doc_content_chars_max=500)
arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv,description="A tool to query arxiv papers")

print(arxiv.name)

arxiv_result = arxiv.invoke("What are the latest papers on graph neural networks?")
print(arxiv_result)

#! Wikipedia API Wrapper
api_wrapper_wikipedia = WikipediaAPIWrapper(top_k_results=2,doc_content_chars_max=500)
wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper_wikipedia,description="A tool to query wikipedia")

print(wikipedia.name)

wikipedia_result = wikipedia.run("capital Of India?")
print(wikipedia_result)
