from pydantic import BaseModel, Field
from typing import List, Optional

class UserQuery(BaseModel):
    message: str
    session_id: str = Field(..., description="Unique ID for this conversation thread")
    
class AgentResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None