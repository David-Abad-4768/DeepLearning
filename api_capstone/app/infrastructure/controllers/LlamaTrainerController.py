import logging
import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.application.services.LlamaTrainerService import LlamaTrainerService

logger = logging.getLogger(__name__)
llama_service = LlamaTrainerService()


class LlamaController:
    def __init__(self):
        self.router = APIRouter(tags=["Llama"])

        # POST /llama/train → public (o protegido con Depends)
        self.router.post(
            "/train",
            status_code=status.HTTP_202_ACCEPTED,
            summary="Inicia el fine-tuning de Llama 3.2-3B con SFT",
            response_model=dict,
        )(self.train)

        # GET /llama/config → devuelve la configuración actual del entrenador
        self.router.get(
            "/config",
            status_code=status.HTTP_200_OK,
            summary="Recupera la configuración de entrenamiento y LoRA",
            response_model=dict,
        )(self.get_config)

    async def train(
        self,
        dataset: UploadFile = File(
            ..., description="Archivo JSONL con campos 'prompt' y 'completion'"
        ),
        epochs: int = Form(1, ge=1),
        lr: float = Form(2e-5, gt=0),
        batch_size: int = Form(1, ge=1),
        grad_accum: int = Form(16, ge=1),
    ):
        logger.info(
            "HTTP POST /llama/train file=%s epochs=%d lr=%f batch_size=%d grad_accum=%d",
            dataset.filename,
            epochs,
            lr,
            batch_size,
            grad_accum,
        )

        # Solo JSONL
        if not dataset.filename.lower().endswith(".jsonl"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe tener extensión .jsonl",
            )

        # Guardar temporalmente
        try:
            suffix = Path(dataset.filename).suffix.lower()
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(dataset.file, tmp)
                tmp_path = Path(tmp.name)
        except Exception:
            logger.exception("Error al guardar temporalmente el JSONL")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo procesar el archivo JSONL",
            )

        # Iniciar o reanudar entrenamiento
        try:
            result = llama_service.train(
                dataset_path=str(tmp_path),
                epochs=epochs,
                lr=lr,
                batch_size=batch_size,
                grad_accum=grad_accum,
                resume_from_checkpoint=str(llama_service.new_model_dir),
            )
        except KeyError:
            logger.exception("JSONL sin campos 'prompt' o 'completion'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El JSONL debe contener claves 'prompt' y 'completion'",
            )
        except Exception:
            logger.exception("Error durante el fine-tuning")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocurrió un error durante el entrenamiento",
            )
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        return {
            "message": "Entrenamiento iniciado correctamente",
            "local_path": result["local_path"],
            "huggingface_repo": result.get("hf_repo") or None,
        }

    async def get_config(self):
        try:
            config = llama_service.get_config()
        except Exception:
            logger.exception("No se pudo obtener la configuración")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo recuperar la configuración de entrenamiento",
            )
        return {"config": config}
