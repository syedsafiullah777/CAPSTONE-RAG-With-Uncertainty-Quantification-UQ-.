"""Hugging Face transformers backend (4-bit preferred on Colab GPU)."""

from __future__ import annotations

import time
from typing import Any

from src.models.types import GenerationResult


class TransformersBackend:
    name = "transformers"

    def __init__(
        self,
        *,
        model_id: str = "Qwen/Qwen3-8B",
        quantisation: str = "bitsandbytes-4bit",
        load_in_4bit: bool = True,
        device_map: str = "auto",
    ) -> None:
        self.model_id = model_id
        self.quantisation = quantisation
        self.load_in_4bit = load_in_4bit
        self.device_map = device_map
        self._model = None
        self._tokenizer = None

    def is_available(self) -> bool:
        try:
            import transformers  # noqa: F401
            import torch  # noqa: F401
        except ImportError:
            return False
        return True

    def _load(self) -> tuple[Any, Any]:
        if self._model is not None and self._tokenizer is not None:
            return self._model, self._tokenizer

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        kwargs: dict[str, Any] = {
            "device_map": self.device_map,
            "trust_remote_code": True,
        }
        if self.load_in_4bit and torch.cuda.is_available():
            try:
                from transformers import BitsAndBytesConfig

                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
                self.quantisation = "bitsandbytes-4bit"
            except Exception:
                kwargs["torch_dtype"] = torch.float16
                self.quantisation = "fp16"
        else:
            kwargs["torch_dtype"] = torch.float16 if torch.cuda.is_available() else torch.float32
            self.quantisation = "fp16" if torch.cuda.is_available() else "fp32"

        self._model = AutoModelForCausalLM.from_pretrained(self.model_id, **kwargs)
        return self._model, self._tokenizer

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.1,
        max_new_tokens: int = 512,
        top_p: float | None = None,
    ) -> GenerationResult:
        import torch

        model, tokenizer = self._load()
        inputs = tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "temperature": max(temperature, 1e-5),
        }
        if top_p is not None:
            gen_kwargs["top_p"] = top_p

        start = time.perf_counter()
        with torch.no_grad():
            output_ids = model.generate(**inputs, **gen_kwargs)
        latency = time.perf_counter() - start
        generated = output_ids[0][inputs["input_ids"].shape[-1] :]
        text = tokenizer.decode(generated, skip_special_tokens=True).strip()
        return GenerationResult(
            text=text,
            model=self.model_id,
            backend=self.name,
            quantisation=self.quantisation,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            latency_seconds=latency,
            prompt_chars=len(prompt),
            finish_reason="stop",
            raw={},
        )
