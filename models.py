from pydantic import BaseModel
from typing import List, Optional

class UserQuery(BaseModel):
    message: str
    session_id: str = "default_session"

class AgentResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None