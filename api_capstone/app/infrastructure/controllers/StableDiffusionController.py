from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from zipfile import BadZipFile, ZipFile

import torch
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.application.models.images.ImageModel import (GenerateRequest,
                                                      GenerateResponse,
                                                      LoadLoraRequest,
                                                      SimpleMessage,
                                                      TrainLoraResponse)
from app.application.services.StableDiffusionGeneratorService import \
    StableDiffusionService

logger = logging.getLogger(__name__)
sd_service = StableDiffusionService()


class StableDiffusionController:
    """Agrupa los endpoints relacionados con Stable Diffusion."""

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/sd", tags=["StableDiffusion"])
        self.router.post("/train-lora", response_model=TrainLoraResponse)(
            self.train_lora
        )
        self.router.post("/generate", response_model=GenerateResponse)(
            self.generate_image
        )
        self.router.post("/load-lora", response_model=SimpleMessage)(self.load_lora)
        self.router.post("/release", response_model=SimpleMessage)(self.release_model)

    async def train_lora(
        self,
        dataset_zip: UploadFile = File(..., description="ZIP con carpeta train/"),
        epochs: int = Form(1, ge=1),
        lr: float = Form(1e-4, gt=0),
        batch_size: int = Form(1, ge=1),
        grad_accum: int = Form(4, ge=1),
        rank: int = Form(8, ge=1),
        repo_id: Optional[str] = Form(None),
    ) -> TrainLoraResponse:
        """Entrena un LoRA a partir de un único ZIP con la carpeta **train/**.

        El ZIP debe contener, por cada imagen, un fichero `.txt` con el prompt.
        Ejemplo de estructura:

        ```
        dataset.zip
        └── train/
            ├── funda-1.jpg
            ├── funda-1.txt
            ├── funda-2.png
            ├── funda-2.txt
            └── ...
        ```
        """

        if not dataset_zip.filename.lower().endswith(".zip"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="dataset_zip must be a .zip archive.",
            )

        tmp_dir = Path(tempfile.mkdtemp())
        zip_path = tmp_dir / "dataset.zip"
        zip_path.write_bytes(await dataset_zip.read())

        # Descomprimir y validar estructura
        try:
            with ZipFile(zip_path) as zf:
                zf.extractall(tmp_dir)
        except BadZipFile:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="dataset_zip is corrupt or invalid.",
            ) from None

        train_dir = tmp_dir / "train"
        if not train_dir.is_dir():
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ZIP must contain a train/ directory with images and prompts.",
            )

        try:
            # Llamada corregida: el primer argumento es la carpeta que contiene `train/`
            result = sd_service.train_lora(
                tmp_dir,
                lr=lr,
                rank=rank,
                batch_size=batch_size,
                epochs=epochs,
                grad_accum=grad_accum,
                repo_id=repo_id,
            )
        finally:
            # Limpieza de temporales
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return TrainLoraResponse(
            message="LoRA training completed successfully",
            lora_path=Path(result["lora_path"]),
            huggingface_repo=result["hf_repo"] or None,
        )

    # ------------------------------------------------------------------ #
    # POST /sd/generate
    # ------------------------------------------------------------------ #
    async def generate_image(self, request: GenerateRequest) -> GenerateResponse:
        try:
            img_path = sd_service.generate(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_inference_steps=request.steps,
                guidance_scale=request.guidance_scale,
                seed=request.seed,
            )
            return GenerateResponse(image_path=img_path)
        except Exception as exc:
            logger.exception("Image generation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while generating the image.",
            ) from exc

    # ------------------------------------------------------------------ #
    # POST /sd/load-lora
    # ------------------------------------------------------------------ #
    async def load_lora(self, body: LoadLoraRequest) -> SimpleMessage:
        try:
            sd_service.load_lora(body.lora_path)
            return SimpleMessage(message="LoRA loaded successfully")
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LoRA file not found.",
            ) from None
        except Exception as exc:
            logger.exception("Failed to load LoRA")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not load the LoRA file.",
            ) from exc

    # ------------------------------------------------------------------ #
    # POST /sd/release
    # ------------------------------------------------------------------ #
    async def release_model(self) -> SimpleMessage:
        try:
            sd_service.pipe.to("cpu")
            import gc

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return SimpleMessage(message="Model released from GPU memory")
        except Exception as exc:
            logger.exception("Failed to release model")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not release the model from memory.",
            ) from exc
