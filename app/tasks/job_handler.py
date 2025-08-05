import os
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError
from app.models.job import Job

class JobHandler:
    @staticmethod
    async def increment_retry_count(job_id):
        try:
            job = await Job.get_or_none(id=job_id)
            if job:
                job.retry_count += 1
                await job.save()
        except DBConnectionError as e:
            print(f"DB connection error updating retry_count: {e}")

    @staticmethod
    async def set_status(job_id, status, media_url=None, error=None):
        try:
            await Tortoise.init(
                db_url=os.getenv("DATABASE_URL"),
                modules={"models": ["app.models.job"]}
            )
            job = await Job.get_or_none(id=job_id)
            if job:
                job.status = status
                if media_url is not None:
                    job.media_url = media_url
                job.error = error
                await job.save()
            await Tortoise.close_connections()
        except Exception as e:
            print(f"DB error updating job status: {e}")
