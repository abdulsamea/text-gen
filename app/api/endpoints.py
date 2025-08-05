from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from app.models.job import Job
from app.tasks.worker import generate_media

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    parameters: dict

class GenerateResponse(BaseModel):
    job_id: UUID
    media_url: str | None

class StatusResponse(BaseModel):
    status: str
    media_url: str | None
    error: str | None

@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    try:
        job = await Job.create(
            prompt=request.prompt,
            parameters=request.parameters,
            status="queued"
        )
        generate_media.delay(str(job.id), request.prompt, request.parameters)
        # Return current media_url after creation (likely None initially, filled after processing)
        return GenerateResponse(job_id=job.id, media_url=job.media_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {e}")

@router.get("/status/{job_id}", response_model=StatusResponse)
async def status(job_id: UUID):
    job = await Job.get_or_none(id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return StatusResponse(
        status=job.status,
        media_url=job.media_url,
        error=job.error
    )
