from fastapi import FastAPI

from src.core.events import lifespan
from src.core.settings import get_settings
from src.middlewares.auth_header_context import AuthHeaderContextMiddleware
from src.modules.documents.routers import router as documents_router

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs",
)

settings = get_settings()

app.add_middleware(AuthHeaderContextMiddleware)

app.include_router(documents_router, prefix="/api-documents")
