import os
from fastapi import FastAPI
from app.api.endpoints import router
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

app = FastAPI(title="Async Media Generation Service")

app.include_router(router)

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["app.models.job"]},
    generate_schemas=True,  # Enable for automatic table creation
    add_exception_handlers=True,
)
