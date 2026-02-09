from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import operator
from meta import MetaEngine
import os
import operator
from dotenv import load_dotenv
from tool import search_unit_info, search_item_info

load_dotenv()


llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-3-flash-preview",
    temperature=0
    )

engine = MetaEngine(data_path="tft_challenger_data.json")
web_search_tool = TavilySearchResults(max_results=3)

@tool
def analyze_meta(unit_name: str) -> str:
    """
    Check local Challenger data for a unit's statistics (Items, Winrate).
    ALWAYS use this tool FIRST before searching the web.
    """
    stats = engine.analyze_unit(unit_name)
    if stats:
        return f"LOCAL DATA FOUND: {stats}"
    else:
        return "NO LOCAL DATA FOUND"
    
@tool
def search_web(query: str) -> str:
    """
    Search the internet for TFT guides, meta snapshots, or patch notes.
    Use this ONLY if local data is missing or insufficient.
    """
    return web_search_tool.invoke(query)

tools = [analyze_meta, search_web, search_unit_info, search_item_info]
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def agent_node(state: AgentState) -> AgentState:
    """The Brain: Decides whether to reply or call a tool"""
    messages = state['messages']

    system_prompt = SystemMessage(content="""
    You are top-class Teamfight Tactics (TFT) pro player. help the user win TFT games.
    If the user asks for build advice, use the 'analyze_meta'
    Don't guess. Use the data., a TFT Coach in LATEST SET.
    
    STRATEGY:
    1. FIRST, check 'analyze_meta' to see what Challengers are playing in our database.
    2. ALWAYS check LATEST SET of Teamfight Tactics before searching the web.
    3. IF the database has good data (Sample size > 0), suggest builds based on that.
    4. IF the database is empty (or the unit is new), use 'search_web' to find the latest guides.
    5. When answering, be specific: "Based on 50 challenger matches..." or "I found a guide online..."
    6. Change the name of items before response if the name is these {
                                "TFT_Item_PowerGauntlet" : "Striker flail",
                                "TFT_Item_FrozenHeart" : "Protector Vow", 
                                "TFT_Item_Redemption" : "Spirit Visage",
                                "TFT_Item_SpectralGauntlet" : "Evenshroud",
                                "TFT_Item_NightHarvester" : "Steadfast Heart",
                                "TFT_Item_StatikkShiv" : "Void staff",
                                "TFT_Item_UnstableConcoction" : "Hand of justice",
                                "TFT_Item_MadredsBloodrazor" : "Giant slayer",
                                "TFT_Item_RapidFireCannon" : "Red buff",
                                "TFT_Item_Leviathan" : "Nashor tooth",
                                "TFT_Item_GuardianAngel" : "Edge of night"}.
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