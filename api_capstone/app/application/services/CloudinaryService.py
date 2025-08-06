from pathlib import Path
from typing import Union

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.infrastructure.Settings import settings


class CloudinaryService:
    def __init__(self) -> None:
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )

    def upload_image(
        self,
        file: Union[UploadFile, str, Path],
        *,
        folder: str = "uploads",
        public_id: str | None = None,
        overwrite: bool = False,
        resource_type: str = "image",
        **options,
    ) -> str:
        upload_source = file.file if isinstance(file, UploadFile) else str(file)

        result = cloudinary.uploader.upload(
            upload_source,
            folder=folder,
            public_id=public_id,
            overwrite=overwrite,
            resource_type=resource_type,
            **options,
        )

        return result["secure_url"]
