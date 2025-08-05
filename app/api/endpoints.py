from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
from app.models.job import Job
from app.tasks.worker import generate_media

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The text prompt to generate an image from.")
    parameters: dict = Field(..., description="Additional generation parameters such as aspect_ratio, output_format.")

class GenerateResponse(BaseModel):
    job_id: UUID = Field(..., description="The unique identifier of the queued image generation job.")
    media_url: str | None = Field(None, description="The URL of the generated image once ready.")

class StatusResponse(BaseModel):
    status: str = Field(..., description="Current status of the job (e.g., queued, completed, failed).")
    media_url: str | None = Field(None, description="URL to generated media if available.")
    error: str | None = Field(None, description="Error message if job failed.")
    

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
