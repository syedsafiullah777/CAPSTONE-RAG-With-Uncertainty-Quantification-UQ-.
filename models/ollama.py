from __future__ import annotations

from config import OLLAMA_MODEL


def generate(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.1) -> str:
    try:
        import ollama
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature},
        )
    except Exception as exc:
        raise RuntimeError(
            f"Could not reach Ollama model '{model}'. Start Ollama and make sure the model is available."
        ) from exc

    return response["message"]["content"].strip()
