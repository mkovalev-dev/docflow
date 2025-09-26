from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        yield
    finally:
        pass
