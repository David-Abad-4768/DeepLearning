from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class CORSMiddlewareConfigurator:
    @staticmethod
    def apply(app: FastAPI):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
