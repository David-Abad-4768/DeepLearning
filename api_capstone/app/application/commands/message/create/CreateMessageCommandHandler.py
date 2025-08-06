import asyncio
import os
import random
from datetime import datetime, timezone
from pathlib import Path

import torch
from fastapi import HTTPException
from mediatr import Mediator

from app.application.commands.message.create.CreateMessageCommand import \
    CreateMessageCommand
from app.application.models.message.MessageModel import (CreateMessageModel,
                                                         CreateMessageResponse,
                                                         Message)
from app.application.services.CloudinaryService import CloudinaryService
from app.application.services.LlamaInferenceService import get_llama_instance
from app.application.services.StableDiffusionGeneratorService import \
    StableDiffusionService
from app.core.utils.Logger import get_logger
from app.domain.entities.Message import MessageEntity, MessageTypeEnum
from app.infrastructure.repositories.MessageRepository import MessageRepository

logger = get_logger(__name__)


@Mediator.handler
class CreateMessageCommandHandler:
    def __init__(self):
        self.repo = MessageRepository.instance()
        self.llama = None
        self.sd_service = None
        self.cloudinary = CloudinaryService()

    async def _ask_llama(self, prompt: str) -> str:
        if self.llama is None:
            self.llama = get_llama_instance()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.llama.chat, prompt)

    async def handle(self, request: CreateMessageCommand) -> CreateMessageResponse:
        dto: CreateMessageModel = request.payload
        logger.info("➜ Chat %s | New CLIENT message (image=%s)", dto.chat_id, dto.image)
        now = datetime.now(tz=timezone.utc)

        client_msg = MessageEntity(
            chat_id=dto.chat_id,
            content=dto.content,
            type=MessageTypeEnum.CLIENT,
            created_at=now,
            image=dto.image,
        )
        self.repo.create(client_msg)

        if dto.image:
            if self.llama is not None:
                try:
                    if hasattr(self.llama, "model"):
                        try:
                            self.llama.model.to("cpu")
                        except Exception:
                            pass
                except Exception:
                    pass
                self.llama.release()
                self.llama = None
                torch.cuda.empty_cache()

            if self.sd_service is None:
                self.sd_service = StableDiffusionService()

            seed = random.randint(0, 2**32 - 1)
            try:
                local_image_path: Path = self.sd_service.generate(
                    prompt=dto.content,
                    negative_prompt=None,
                    num_inference_steps=30,
                    guidance_scale=8.0,
                    seed=seed,
                )
                logger.info("Imagen generada en: %s (seed=%s)", local_image_path, seed)
            except Exception as e:
                logger.exception("Error generando imagen con Stable Diffusion")
                raise HTTPException(
                    status_code=500, detail="Error al generar la imagen"
                ) from e

            try:
                secure_url: str = self.cloudinary.upload_image(
                    local_image_path,
                    folder="chat_images",
                    public_id=None,
                    overwrite=False,
                    resource_type="image",
                )
                logger.info("Imagen subida a Cloudinary: %s", secure_url)
            except Exception as e:
                logger.exception("Error subiendo imagen a Cloudinary")
                raise HTTPException(
                    status_code=500, detail="Error al subir la imagen a Cloudinary"
                ) from e

            try:
                os.remove(local_image_path)
                torch.cuda.empty_cache()
            except Exception:
                pass

            try:
                if (
                    self.sd_service is not None
                    and hasattr(self.sd_service, "pipe")
                    and self.sd_service.pipe is not None
                ):
                    self.sd_service.pipe.to("cpu")
                    torch.cuda.empty_cache()
            except Exception:
                pass

            system_msg = MessageEntity(
                chat_id=dto.chat_id,
                content=secure_url,
                type=MessageTypeEnum.SYSTEM,
                created_at=now,
                image=True,
            )
        else:
            if self.sd_service is not None:
                try:
                    self.sd_service.pipe.to("cpu")
                    torch.cuda.empty_cache()
                except Exception:
                    pass
                self.sd_service = None

            try:
                system_text: str = await self._ask_llama(dto.content)
            except Exception as e:
                logger.exception("Error consultando a LLaMA")
                raise HTTPException(
                    status_code=500, detail="Error al contactar con LLaMA"
                ) from e

            system_msg = MessageEntity(
                chat_id=dto.chat_id,
                content=system_text,
                type=MessageTypeEnum.SYSTEM,
                created_at=now,
                image=False,
            )

        self.repo.create(system_msg)

        client_model = Message.model_validate(client_msg, from_attributes=True)
        system_model = Message.model_validate(system_msg, from_attributes=True)

        return CreateMessageResponse(
            client_message=client_model,
            system_message=system_model,
            message="Messages created successfully.",
        )
