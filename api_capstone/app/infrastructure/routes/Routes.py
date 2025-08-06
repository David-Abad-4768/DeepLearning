from fastapi import FastAPI
from mediatr import Mediator

from app.infrastructure.controllers.AuthController import AuthController
from app.infrastructure.controllers.ChatController import ChatController
from app.infrastructure.controllers.LlamaInferenceController import \
    InferenceController
from app.infrastructure.controllers.LlamaTrainerController import \
    LlamaController
from app.infrastructure.controllers.MessageController import MessageController
from app.infrastructure.controllers.StableDiffusionController import \
    StableDiffusionController
from app.infrastructure.controllers.UserController import UserController


def include_routes(app: FastAPI, mediator: Mediator):
    app.include_router(UserController(mediator).router, prefix="/api/v1/user")
    app.include_router(ChatController(mediator).router, prefix="/api/v1/chat")
    app.include_router(MessageController(mediator).router, prefix="/api/v1/message")
    app.include_router(LlamaController().router, prefix="/api/v1/llama")
    app.include_router(InferenceController().router, prefix="/api/v1/llama")
    app.include_router(AuthController().router, prefix="/api/v1/auth")
    app.include_router(StableDiffusionController().router, prefix="/api/v1/staff")
