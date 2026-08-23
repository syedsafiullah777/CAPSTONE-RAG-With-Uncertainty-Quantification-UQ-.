"""Phase 11 live-demo runtime guard: no silent mock fallback."""

from __future__ import annotations

import platform

import pytest

from src.models.factory import create_backend
from src.models.llama_cpp_backend import LlamaCppBackend
from src.models.mock_backend import MockBackend
from src.models.runtime_guard import (
    LiveRuntimeError,
    assert_not_mock_backend,
    is_colab_runtime,
    live_demo_locked,
    mock_forbidden,
    verify_live_llama_cpp_runtime,
)
from src.rag.live import run_live_comparison


def test_mock_forbidden_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("V2_FORBID_MOCK", raising=False)
    monkeypatch.delenv("V2_LIVE_BACKEND", raising=False)
    assert mock_forbidden() is False
    monkeypatch.setenv("V2_FORBID_MOCK", "1")
    assert mock_forbidden() is True
    monkeypatch.delenv("V2_FORBID_MOCK", raising=False)
    monkeypatch.setenv("V2_LIVE_BACKEND", "llama_cpp")
    assert mock_forbidden() is True


def test_assert_not_mock_backend_raises_when_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("V2_FORBID_MOCK", "1")
    with pytest.raises(LiveRuntimeError, match="Mock backend is forbidden"):
        assert_not_mock_backend("mock")


def test_factory_forces_llama_cpp_when_mock_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("V2_FORBID_MOCK", "1")
    backend = create_backend({"backend": "mock"})
    assert isinstance(backend, LlamaCppBackend)
    assert backend.name == "llama_cpp"


def test_factory_still_allows_mock_without_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("V2_FORBID_MOCK", raising=False)
    monkeypatch.delenv("V2_LIVE_BACKEND", raising=False)
    backend = create_backend({"backend": "mock"})
    assert isinstance(backend, MockBackend)


def test_colab_helpers_false_on_macos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("V2_FORBID_MOCK", raising=False)
    monkeypatch.delenv("V2_LIVE_BACKEND", raising=False)
    if platform.system() == "Darwin":
        assert is_colab_runtime() is False
        assert live_demo_locked() is False


def test_factory_forces_llama_cpp_over_ollama_when_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("V2_FORBID_MOCK", "1")
    backend = create_backend({"backend": "ollama_dev"})
    assert isinstance(backend, LlamaCppBackend)
    assert backend.name == "llama_cpp"


def test_verify_live_runtime_rejects_macos() -> None:
    if platform.system() != "Darwin":
        pytest.skip("macOS-only rejection check")
    with pytest.raises(LiveRuntimeError, match="macOS"):
        verify_live_llama_cpp_runtime(require_cuda=True)


def test_live_comparison_refuses_mock_instance_when_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("V2_FORBID_MOCK", "1")
    with pytest.raises(LiveRuntimeError, match="Mock backend is forbidden"):
        run_live_comparison(
            "What is the return on the S&P 500?",
            question_source="fresh",
            backend=MockBackend(canned="should not be used"),
            backend_name="mock",
            run_id="phase11_guard",
        )
