from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from utils.generate_thread_id import generate_thread_id
from redis_checkpointer import get_checkpointer
from dotenv import load_dotenv
from langgraph.graph import add_messages
from system_prompt import SYSTEM_PROMPT
import logging
from tools.db.add_to_db import add_to_db
from tools.db.retrieve_from_db import retrieve_from_db

logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()

MODEL_NAME = "gpt-3.5-turbo"

llm = ChatOpenAI(
            model_name=MODEL_NAME, temperature=0.7)

tools = [add_to_db, retrieve_from_db]

model = llm.bind_tools(tools)


class ChatbotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: ChatbotState):
    if len(state["messages"]) == 1:  
        state["messages"].insert(0, SystemMessage(content=SYSTEM_PROMPT.format(user_id=thread_id)))
    return {"messages": [model.invoke(state["messages"])]}

def route_tools(state: ChatbotState):
    """Determine whether to use tools or end the conversation based on the last message.

    Args:
        state (ChatbotState): The current state of the conversation.

    Returns:
        Literal["tools", "end"]: The next step in the graph.
    """
    msg = state["messages"][-1]
    if msg.tool_calls:
        return "tools"

    return END

graph_builder = StateGraph(ChatbotState)

# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))

# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", route_tools, ["tools", END])
graph_builder.add_edge("tools", "chatbot")

checkpointer = get_checkpointer()

graph = graph_builder.compile(checkpointer=checkpointer)

thread_id = generate_thread_id()

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        config: RunnableConfig = {'thread_id': thread_id}
        response = graph.invoke(input={"messages": [HumanMessage(content=user_input)]}, config=config)
        print("AI:", response["messages"][-1].content)
        
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        print("An error occurred. Please try again.")
        break




