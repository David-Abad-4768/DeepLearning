from pathlib import Path
from typing import Any, Dict, Optional

import unsloth
from transformers.training_args import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel, is_bf16_supported

from datasets import Dataset, load_dataset


class LlamaTrainerService:

    def __init__(
        self,
        src_model: str = "unsloth/Llama-3.2-3B-Instruct",
        new_model_dir: str = "New-Llama-3.2-3B-trained",
        max_seq_len: int = 2048,
    ) -> None:
        self.src_model = src_model
        self.new_model_dir = new_model_dir
        self.max_seq_len = max_seq_len

    @staticmethod
    def _chat_template(message: str) -> str:
        return (
            "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
            f"<|im_start|>user\n{message}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

    def _prepare_dataset(
        self,
        jsonl_path: str,
    ) -> Dataset:
        ds = load_dataset("json", data_files=jsonl_path, split="train")

        def _format(ex: Dict[str, str]) -> Dict[str, str]:
            prompt = ex["prompt"]
            completion = ex["completion"]
            full = (
                "<|im_start|>system\nEres un asistente útil experto en smartphones.<|im_end|>\n"
                f"<|im_start|>user\n{prompt}<|im_end|>\n"
                f"<|im_start|>assistant\n{completion}<|im_end|>"
            )
            return {"text": full}

        return ds.map(_format, remove_columns=ds.column_names)

    def train(
        self,
        dataset_path: str,
        *,
        epochs: int = 1,
        lr: float = 2e-5,
        batch_size: int = 1,
        grad_accum: int = 16,
        save_steps: int = 250,
        log_steps: int = 50,
        resume_from_checkpoint: Optional[str] = None,
        push_to_hub: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Fine-tunes the model using the dataset at dataset_path (CSV or JSONL).
        If resume_from_checkpoint is provided, continues from the latest checkpoint.
        Returns a dictionary with the final status.
        """
        # Load base model
        print("[+] Loading 4-bit base model …")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.src_model,
            load_in_4bit=True,
            dtype=None,
        )

        # Inject LoRA adapters
        print("[+] Injecting LoRA adapters …")
        r, lora_alpha, lora_dropout, bias = 8, 16, 0.05, "none"
        target_modules = [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
        model = FastLanguageModel.get_peft_model(
            model,
            r=r,
            target_modules=target_modules,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias=bias,
            use_gradient_checkpointing="unsloth",
        )

        # Prepare dataset
        print("[+] Preparing dataset …")
        train_ds = self._prepare_dataset(dataset_path)

        # Training arguments
        print("[+] Building TrainingArguments …")
        args = TrainingArguments(
            output_dir=self.new_model_dir,
            learning_rate=lr,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum,
            bf16=False,
            fp16=False,
            logging_steps=log_steps,
            save_steps=save_steps,
            save_total_limit=2,
            report_to="none",
        )

        # Trainer
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=train_ds,
            args=args,
            dataset_text_field="text",
        )

        # Start or resume training
        print("[+] Starting fine-tuning …")
        if resume_from_checkpoint:
            # Solución: especificar el checkpoint exacto
            resume_from_checkpoint = str(Path(self.new_model_dir) / "checkpoint-100")
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        else:
            trainer.train()

        # Save artifacts
        print("[+] Saving artifacts …")
        out_dir = Path(self.new_model_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)

        return {
            "status": "completed",
            "local_path": str(out_dir.resolve()),
            "hf_repo": push_to_hub or "",
        }
