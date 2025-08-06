import gc
from pathlib import Path
from typing import Optional

import torch
from transformers import GenerationConfig
from unsloth import FastLanguageModel

_LLAMA_INSTANCE: Optional[FastLanguageModel] = None
_TOKENIZER_INSTANCE = None


def get_llama_instance(
    model_dir: str = "New-Llama-3.2-3B-trained/checkpoint-100",
) -> "LlamaService":
    global _LLAMA_INSTANCE, _TOKENIZER_INSTANCE

    if _LLAMA_INSTANCE is None or _TOKENIZER_INSTANCE is None:
        print("🦥 Inicializando LlamaInferenceService…")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=Path(model_dir).as_posix(),
            load_in_4bit=True,
            dtype=None,
            device_map="auto",
        )
        model.eval()
        _LLAMA_INSTANCE, _TOKENIZER_INSTANCE = model, tokenizer

    class LlamaService:
        def __init__(self, model, tokenizer):
            self.model = model
            self.tokenizer = tokenizer
            self.template = (
                "<|im_start|>system\n"
                "Eres un asistente **experto exclusivamente** en smartphones y celulares. "
                "Responde únicamente preguntas sobre marcas, modelos, especificaciones técnicas, precios y comparativas.\n"
                "Si la pregunta NO trata de smartphones, debes responder EXACTAMENTE:\n"
                '"Lo siento, solo puedo responder preguntas sobre smartphones y celulares."\n'
                "No añadas nada más.\n\n"
                "### Ejemplos de comportamiento:\n"
                "User: ¿Qué versión de Bluetooth tiene el Samsung M3310?\n"
                "Assistant: Bluetooth 2.1.\n\n"
                "User: ¿Cómo se calcula el interés compuesto?\n"
                "Assistant: Lo siento, solo puedo responder preguntas sobre smartphones y celulares.\n"
                "<|im_end|>\n"
                "<|im_start|>user\n{msg}\n<|im_end|>\n"
                "<|im_start|>assistant\n"
            )
            self.gen_cfg = GenerationConfig(
                max_new_tokens=256,
                do_sample=False,
                repetition_penalty=1.0,
            )

        def chat(self, question: str) -> str:
            prompt = self.template.format(msg=question)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            try:
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        generation_config=self.gen_cfg,
                    )
                raw = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                resp = raw.split("<|im_start|>assistant")[-1].strip()
                refusal = "Lo siento, solo puedo responder preguntas sobre smartphones y celulares."
                if resp == refusal or not resp:
                    return refusal
                return resp
            finally:
                self.release()

        def release(self):
            global _LLAMA_INSTANCE, _TOKENIZER_INSTANCE
            try:
                del self.model, self.tokenizer
            except NameError:
                pass
            _LLAMA_INSTANCE = None
            _TOKENIZER_INSTANCE = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    return LlamaService(_LLAMA_INSTANCE, _TOKENIZER_INSTANCE)
