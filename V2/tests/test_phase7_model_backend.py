"""Phase 7 tests: fingerprint + backend factory (mock) + smoke validation evidence."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import project_root
from src.models.factory import create_backend
from src.models.fingerprint import collect_fingerprint
from src.models.mock_backend import MockBackend


def test_fingerprint_has_core_fields() -> None:
    fp = collect_fingerprint(model_config={"name": "Qwen3-8B", "backend": "mock"}, project_root=str(project_root()))
    assert "platform" in fp
    assert "device" in fp
    assert "model_config" in fp
    assert fp["model_config"]["name"] == "Qwen3-8B"
    assert "packages" in fp


def test_mock_backend_generate() -> None:
    backend = create_backend({"backend": "mock"})
    assert isinstance(backend, MockBackend)
    result = backend.generate("hello", temperature=0.0, max_new_tokens=16)
    assert result.backend == "mock"
    assert "MOCK_ANSWER" in result.text
    assert result.prompt_chars == 5


def test_factory_ollama_name() -> None:
    backend = create_backend({"backend": "ollama_dev", "ollama_model": "qwen3:8b"})
    assert backend.name == "ollama_dev"


def test_phase7_smoke_validation_artefact_if_present() -> None:
    root = project_root()
    smoke = root / "results" / "config" / "phase7_smoke_test.json"
    fp = root / "results" / "config" / "phase7_runtime_fingerprint.json"
    assert smoke.is_file(), "Run: PYTHONPATH=. python scripts/smoke_generate.py --backend ollama_dev|mock"
    assert fp.is_file()
    data = json.loads(smoke.read_text(encoding="utf-8"))
    assert data["phase"] == 7
    assert data["test_name"] == "phase7_llm_generation_smoke"
    assert data["status"] in {"PASS", "FAIL", "NEEDS_VERIFICATION"}
    extra = data.get("extra") or {}
    gen = extra.get("generation") or {}
    assert str(data.get("actual") or gen.get("text") or "").strip()
    assert (extra.get("backend_used") or gen.get("backend")) in {
        "ollama_dev",
        "llama_cpp",
        "transformers",
        "mock",
    }
    fp_data = json.loads(fp.read_text(encoding="utf-8"))
    assert "device" in fp_data
