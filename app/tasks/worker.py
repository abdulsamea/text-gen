import os
import asyncio
from celery import Celery, Task
from dotenv import load_dotenv
from io import BytesIO
import re
from app.tasks.job_handler import JobHandler
from app.tasks.media_client import MediaClient
from app.tasks.retry_handler import RetryHandler
from PIL import Image, ImageDraw, ImageFont
from app.tasks.replicate_client import ReplicateClient

load_dotenv()

REDIS_BROKER_URL = os.getenv("REDIS_URL")
celery_app = Celery("tasks", broker=REDIS_BROKER_URL)
media_client = MediaClient()
replicate_client = ReplicateClient()

class MediaGenerationTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_backoff_max = 60

    def run(self, job_id, prompt, parameters):
        return asyncio.run(self.async_run(job_id, prompt, parameters))

    async def async_run(self, job_id, prompt, parameters):
        try:
            print(f"Starting generate_media with exponential backoff for job_id: {job_id}")
            safe_prompt = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:50]
            filename = f"output_{safe_prompt}.png"

            async def text_to_image_generation():
                # Call replicate API to generate image bytes
                return replicate_client.generate_image(prompt, parameters)

            image_bytes = await RetryHandler.run_with_exponential_backoff(
                text_to_image_generation,
                max_retries=5,
                base_delay=1,
                max_delay=60
            )

            buf = BytesIO(image_bytes)
            buf.seek(0)

            async def s3_upload():
                s3_url = media_client.upload_image(filename, buf)
                return s3_url

            s3_url = await RetryHandler.run_with_exponential_backoff(
                s3_upload,
                max_retries=5,
                base_delay=1,
                max_delay=60
            )

            async def db_update():
                await JobHandler.set_status(job_id, "completed", media_url=s3_url, error=None)

            await RetryHandler.run_with_exponential_backoff(
                db_update,
                max_retries=5,
                base_delay=1,
                max_delay=60
            )

            return s3_url

        except Exception as exc:
            await JobHandler.set_status(job_id, "failed", error=str(exc))
            raise

generate_media = celery_app.register_task(MediaGenerationTask())
