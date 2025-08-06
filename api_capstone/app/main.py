"""Main entry point of the FastAPI application."""

import os
import pathlib
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from mediatr import Mediator

import app.application.commands as command_pkg
from app.application.commands.chat.create.CreateChatCommandHandler import \
    CreateChatCommandHandler
from app.application.commands.chat.delete.DeleteChatCommandHandler import \
    DeleteChatCommandHandler
from app.application.commands.chat.update.UpdateChatCommandHandler import \
    UpdateChatTitleCommandHandler
from app.application.commands.message.create.CreateMessageCommandHandler import \
    CreateMessageCommandHandler
from app.application.commands.user.create.CreateUserCommandHandler import \
    CreateCommandHandler
from app.application.queries.chat.get_by_user.GetChatsByUserQueryHandler import \
    GetChatsByUserQueryHandler
from app.application.queries.message.get_messages_paged_query.GetMessagesPagedQueryHandler import \
    GetMessagesPagedQueryHandler
from app.core.utils.HandlerLoader import load_handlers
from app.core.utils.Logger import get_logger
from app.infrastructure.database.Database import init_db
from app.infrastructure.middlewares.CorsMiddleware import \
    CORSMiddlewareConfigurator
from app.infrastructure.middlewares.ResponseWrapperMiddleware import \
    ResponseWrapperMiddleware
from app.infrastructure.routes.Routes import include_routes

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize database when app starts."""
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Finnisimo Chat V2", version="2.0.0", lifespan=lifespan)

    CORSMiddlewareConfigurator.apply(app)
    app.add_middleware(ResponseWrapperMiddleware)

    load_handlers(command_pkg)
    mediator = Mediator()

    include_routes(app, mediator)

    @app.get("/", include_in_schema=False)
    async def root():
        logger.info("Redirect to docs")
        return RedirectResponse("/docs")

    return app


app = create_app()
if __name__ == "__main__":
    cert_dir = pathlib.Path(__file__).resolve().parent.parent / "certificates"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"

    use_ssl = cert_file.exists() and key_file.exists()
    port = 8443 if use_ssl else 8080

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        ssl_certfile=str(cert_file) if use_ssl else None,
        ssl_keyfile=str(key_file) if use_ssl else None,
    )
