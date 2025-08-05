import os
import asyncio
from celery import Celery, Task
from dotenv import load_dotenv
from io import BytesIO
import re
from app.tasks.job_handler import JobHandler
from app.tasks.media_client import MediaClient
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

REDIS_BROKER_URL = os.getenv("REDIS_URL")
celery_app = Celery("tasks", broker=REDIS_BROKER_URL)
media_client = MediaClient()

class MediaGenerationTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_backoff_max = 60

    def run(self, job_id, prompt, parameters):
        # Celery runs this in a sync context; bridge to async.
        return asyncio.run(self.async_run(job_id, prompt, parameters))

    async def async_run(self, job_id, prompt, parameters):
        try:
            print(f"Starting generate_media with exponential backoff for job_id: {job_id}")
            safe_prompt = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:50]
            filename = f"output_{safe_prompt}.png"

            # Create image
            img = Image.new('RGB', (512, 512), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            d.text((10, 250), prompt, fill=(255, 255, 0), font=font)
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)

            for attempt in range(1, 6):
                try:
                    s3_url = media_client.upload_image(filename, buf)
                    print(f"Uploaded simple image to {s3_url}")
                    break
                except Exception as e:
                    print(f"S3 upload attempt {attempt} failed: {e}")
                    await JobHandler.increment_retry_count(job_id)
                    if attempt == 5:
                        raise
                    await asyncio.sleep(2 ** attempt)
                    buf.seek(0)

            for attempt in range(1, 6):
                try:
                    await JobHandler.set_status(job_id, "completed", media_url=s3_url, error=None)
                    break
                except Exception as e:
                    print(f"DB update attempt {attempt} failed: {e}")
                    await JobHandler.increment_retry_count(job_id)
                    if attempt == 5:
                        raise
                    await asyncio.sleep(2 ** attempt)

            return s3_url
        except Exception as exc:
            await JobHandler.set_status(job_id, "failed", error=str(exc))
            raise

generate_media = celery_app.register_task(MediaGenerationTask())
