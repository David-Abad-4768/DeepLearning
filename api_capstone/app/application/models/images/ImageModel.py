from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt positivo para la generación")
    negative_prompt: Optional[str] = Field(
        None, description="Prompt negativo para la generación"
    )
    steps: int = Field(25, ge=1, le=50, description="Número de pasos de inferencia")
    guidance_scale: float = Field(7.5, gt=0, description="CFG guidance scale")
    seed: Optional[int] = Field(None, description="Semilla RNG (reproducible)")

    model_config = ConfigDict(from_attributes=True)


class GenerateResponse(BaseModel):
    image_path: Path | HttpUrl

    model_config = ConfigDict(from_attributes=True)


class LoadLoraRequest(BaseModel):
    lora_path: Path

    model_config = ConfigDict(from_attributes=True)


class SimpleMessage(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)


class TrainLoraResponse(BaseModel):
    lora_path: Path
    huggingface_repo: Optional[str] = None
    message: str

    model_config = ConfigDict(from_attributes=True)
