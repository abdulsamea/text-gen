# app/api/schemas.py
from pydantic import BaseModel, Field
from typing import Dict, Optional
import uuid

class GenerateRequest(BaseModel):
    prompt: str
    parameters: Dict

class GenerateResponse(BaseModel):
    job_id: uuid.UUID

class StatusResponse(BaseModel):
    status: str
    media_url: Optional[str]
    error: Optional[str]
