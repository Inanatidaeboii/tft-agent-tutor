from fastapi import FastAPI, HTTPException, BackgroundTasks
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from fastapi.middleware.cors import CORSMiddleware
from agent_graph import app as agent_app
from models import UserQuery, AgentResponse
from data_pipeline import run_pipeline

app = FastAPI(title="TFT Coach Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def health_check():
    """Simple health check endpoint."""
    return {"status": "active", "service": "TFT Coach Agent"}

@app.post("/chat", response_model=AgentResponse)
def chat_endpoint(query: UserQuery):
    """
    Send a message to the Agent.
    """
    try:
        config = {"configurable": {"thread_id": query.session_id}}        
        inputs = {"messages": [HumanMessage(content=query.message)]}
        results = agent_app.invoke(inputs, config=config)

        last_message = results['messages'][-1]
        
        tool_names = []

        for msg in results['messages']:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_names.append(tool_call['name'])
        
        tool_used = ", ".join(tool_names) if tool_names else None
        return AgentResponse(
            response=last_message.text,
            tool_used=tool_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/refresh-data")
def trigger_data_refresh(background_tasks: BackgroundTasks):
    """
    Triggers the Riot API scraper in the background.
    Returns immediately so the user doesn't wait.
    """
    background_tasks.add_task(run_pipeline)
    return {"status": "accepted", "message": "Data refresh started in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)