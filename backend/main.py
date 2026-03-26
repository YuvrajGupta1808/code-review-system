"""FastAPI application entry point."""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import load_settings
from backend.event_bus import get_event_bus
from backend.routes.health import router as health_router
from backend.routes.streaming import router as streaming_router

# Load environment variables before any other imports that use settings
load_dotenv()

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Loads settings from environment, attaches event bus and settings to app.state
    so that route handlers can access them.
    """
    settings = load_settings()
    bus = get_event_bus()

    app = FastAPI(title="Code Review System", version="0.1.0")

    # Attach settings and bus to app state for route handlers
    app.state.settings = settings
    app.state.bus = bus

    # Configure CORS with frontend URL from settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    app.include_router(health_router)
    app.include_router(streaming_router)

    return app


if __name__ == "__main__":
    import uvicorn

    settings = load_settings()
    logger.info(
        f"Starting server on {settings.backend_host}:{settings.backend_port} "
        f"with log level {settings.log_level}"
    )
    app = create_app()
    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level=settings.log_level,
    )
