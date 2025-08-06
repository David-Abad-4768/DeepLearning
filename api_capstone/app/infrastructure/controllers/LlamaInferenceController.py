import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.application.services.LlamaInferenceService import get_llama_instance

logger = logging.getLogger(__name__)


class QueryModel(BaseModel):
    question: str


class InferenceController:
    def __init__(self):
        self.router = APIRouter(tags=["Llama"])
        self.router.post("/ask", status_code=status.HTTP_200_OK)(self.ask)
        self.router.post("/release", status_code=status.HTTP_200_OK)(self.release_model)

    async def ask(self, query: QueryModel):
        logger.info("HTTP POST /v1/llama/ask question=%s", query.question[:50])
        try:
            llama = get_llama_instance()
            answer = llama.chat(query.question)
            return {"answer": answer}
        except HTTPException:
            raise
        except Exception:
            logger.exception("Inference failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while generating the answer",
            )

    async def release_model(self):
        try:
            llama = get_llama_instance()
            llama.release()
            logger.info("Llama model released from GPU memory")
            return {"message": "Modelo liberado de memoria GPU"}
        except Exception:
            logger.exception("Error releasing model")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo liberar el modelo de memoria",
            )
