from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
import operator
from meta import MetaEngine
import os
import operator
from dotenv import load_dotenv
from tool import search_unit_info

load_dotenv()


llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-3-flash-preview",
    temperature=0
    )

engine = MetaEngine(data_patch="tft_challenger_data.json")

@tool
def get_bis(unit_name:str) -> str:
    """
    Use this tool to find the best-in-slot items for a specific TFT unit.
    Args:
        unit_name: The name of the unit (e.g., 'Jinx', 'Vi', 'Warwick').
    Returns:
        A string containing the top items and their frequency.
    """
    print(f"Tool Triggered: Searching for {unit_name}...")

    formatted_name = f"TFT16_{unit_name.capitalize()}"

    return str(engine.get_best_items(formatted_name))

tools = [get_bis, search_unit_info]

llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def agent_node(state: AgentState) -> AgentState:
    """The Brain: Decides whether to reply or call a tool"""
    messages = state['messages']

    system_prompt = SystemMessage(content="""
    You are top-class Teamfight Tactics (TFT) pro player. help the user win TFT games.
    If the user asks for build advice, use the 'get_bis'
    Don't guess. Use the data.
    """)

    response = llm_with_tools.invoke([system_prompt] + messages)
    return {"messages":[response]}

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)

tool_node = ToolNode(tools)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

def should_continue(state: AgentState) -> str:
    messages = state['messages']
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    
    return END

workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()

print("Ask a question about TFT builds!")

while True:
    try:
        user_input = input("\nYour question: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        inputs = {"messages": [HumanMessage(content=user_input)]}

        for event in app.stream(inputs):
            for k, v in event.items():
                print(f"Node: {k}")
                if k == "agent":
                    msg = v["messages"][0]
                    if msg.tool_calls:
                        print(f"    Tool Calls: {msg.tool_calls[0]['name']}")
                        print(f"    Args: {msg.tool_calls[0]['args']}")
                    else:
                        print(f"    Response: {msg.content}")

                elif k == "tools":
                    print(f"    Tool Results: {v['messages'][0].content}")
    except Exception as e:
        print(f"❌ Error: {e}")