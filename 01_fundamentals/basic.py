from langgraph.graph import StateGraph, MessagesState, START, END

#! Simple Node
def welcome(state: MessagesState):
    return {
        "messages": [{"role": "ai", "content": "Hello! Welcome to LangGraph"}]
    }

#! Simple Graph
graph = StateGraph(MessagesState)


#! add nodes to the graph
graph.add_node(welcome)


#! Connect flow
graph.add_edge(START, "welcome")
graph.add_edge("welcome", END)


#! compile the graph
app = graph.compile()

#! visualize the graph

#! visualize the graph (SAFE)
app.get_graph().print_ascii()
print(app.get_graph().draw_mermaid())


#! run the graph
result = app.invoke({"messages": [{"role": "user", "content": "Ho"}]})

print(result)