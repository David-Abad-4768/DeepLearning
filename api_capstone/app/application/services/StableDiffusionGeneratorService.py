# app/application/services/StableDiffusionGeneratorService.py

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union

import torch
from PIL import Image

from diffusers import StableDiffusionPipeline

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"
torch.backends.cudnn.enabled = False

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


class StableDiffusionService:
    def __init__(
        self,
        model_id: Union[str, Path] = "runwayml/stable-diffusion-v1-5",
        output_dir: str = "generated_images",
        *,
        use_fp16: bool = True,
        variant: Optional[str] = None,
        use_safetensors: bool = False,
    ) -> None:
        self.model_id = str(model_id)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        dtype = (
            torch.float16 if use_fp16 and torch.cuda.is_available() else torch.float32
        )

        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            safety_checker=None,
            feature_extractor=None,
            requires_safety_checker=False,
            use_safetensors=use_safetensors,
            variant=variant,
        )

        if torch.cuda.is_available():
            self.pipe.enable_model_cpu_offload()
            self.pipe.enable_attention_slicing()

    def generate(
        self,
        prompt: str,
        *,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5,
        height: int = 512,
        width: int = 512,
        seed: Optional[int] = None,
    ) -> Path:
        generator = torch.manual_seed(seed) if seed is not None else None

        image: Image.Image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            height=height,
            width=width,
            generator=generator,
        ).images[0]

        safe_name = (
            prompt[:50]
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )
        out_path = self.output_dir / f"{safe_name}.png"
        image.save(out_path)
        return out_path

    def train_lora(
        self,
        dataset_root: Union[str, Path],
        *,
        output_dir: Union[str, Path] = "sd_lora_trained",
        resolution: int = 64,
        lr: float = 1e-4,
        rank: int = 2,
        batch_size: int = 1,
        epochs: int = 1,
        grad_accum: int = 1,
        save_steps: int = 100,
        repo_id: Optional[str] = None,
    ) -> Dict[str, str]:
        dataset_root = Path(dataset_root)
        train_dir = dataset_root / "train"
        if not train_dir.is_dir():
            raise FileNotFoundError("El ZIP debe incluir la carpeta train/")

        imagenes = [p for p in train_dir.iterdir() if p.suffix.lower() in IMG_EXTS]
        if not imagenes:
            raise FileNotFoundError("No se encontraron imágenes dentro de train/")

        # --- Create metadata.jsonl ---
        jsonl_path = train_dir / "metadata.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as writer:
            for img_path in imagenes:
                text_path = img_path.with_suffix(".txt")
                if not text_path.exists():
                    raise FileNotFoundError(f"Falta .txt para {img_path.name}")
                caption = text_path.read_text(encoding="utf-8").strip()
                writer.write(
                    json.dumps(
                        {"file_name": img_path.name, "text": caption},
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        script_path = Path(
            "diffusers/examples/text_to_image/train_text_to_image_lora.py"
        )
        if not script_path.exists():
            raise FileNotFoundError(
                "Falta el script train_text_to_image_lora.py en la raíz"
            )

        del self.pipe
        torch.cuda.empty_cache()

        cmd = [
            "accelerate",
            "launch",
            str(script_path),
            "--pretrained_model_name_or_path",
            self.model_id,
            "--train_data_dir",
            str(train_dir),
            "--image_column",
            "image",
            "--caption_column",
            "text",
            "--output_dir",
            str(output_dir),
            "--resolution",
            str(resolution),
            "--learning_rate",
            str(lr),
            "--rank",
            str(rank),
            "--train_batch_size",
            str(batch_size),
            "--gradient_accumulation_steps",
            str(grad_accum),
            "--num_train_epochs",
            str(epochs),
            "--mixed_precision",
            "fp16",
            "--gradient_checkpointing",
            "--checkpointing_steps",
            str(save_steps),
            "--use_8bit_adam",
        ]
        if repo_id:
            cmd += ["--push_to_hub", "--hub_model_id", repo_id]

        try:
            completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("=== STDOUT de accelerate ===\n", completed.stdout)
            print("=== STDERR de accelerate ===\n", completed.stderr)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"LoRA falló con código {e.returncode}.\n"
                f"=== STDOUT ===\n{e.stdout or '(vacío)'}\n\n"
                f"=== STDERR ===\n{e.stderr or '(vacío)'}"
            ) from None

        return {
            "status": "completed",
            "lora_path": str(Path(output_dir).resolve()),
            "hf_repo": repo_id or "",
        }
