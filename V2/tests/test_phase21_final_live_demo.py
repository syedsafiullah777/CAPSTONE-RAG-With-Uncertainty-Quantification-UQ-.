"""Static checks for the Phase 21 Colab final live-demo launcher notebook.

Does not run Streamlit, RAG, Qwen, calibration, the judge, or the 420-case benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK = Path("notebooks/colab_phase21_final_live_demo.ipynb")


def _notebook_text() -> str:
    payload = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in payload.get("cells") or []:
        source = cell.get("source") or []
        if isinstance(source, list):
            chunks.append("".join(source))
        else:
            chunks.append(str(source))
    return "\n".join(chunks)


def test_phase21_notebook_json_is_valid() -> None:
    payload = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert payload.get("nbformat") == 4
    cells = payload.get("cells") or []
    assert len(cells) >= 8
    assert any(c.get("cell_type") == "code" for c in cells)


def test_phase21_launcher_uses_streamlit_entrypoint_and_gpu_guard() -> None:
    text = _notebook_text()
    assert "app/streamlit_app.py" in text
    assert "streamlit" in text
    assert "--server.port=8501" in text
    assert "proxyPort(8501)" in text
    assert "serve_kernel_port_as_iframe" in text
    assert "verify_live_llama_cpp_runtime" in text
    assert "V2_LIVE_BACKEND" in text
    assert "llama_cpp" in text
    assert "V2_FORBID_MOCK" in text
    assert "Tesla T4" in text
    assert "Q4_K_M" in text
    assert "T=0.65 LOCKED" in text
    assert "V2 FINAL LIVE DEMO" in text
    assert "MyDrive/MSc-RAG/artifacts/knowledge_base" in text
    assert "validate_index_preflight" in text
    assert "Live RAG Demo" in text
    assert "Benchmark Results" in text
    assert "Benchmark Questions" in text
    assert "Refusing to launch" in text or "Refusing to start Streamlit" in text
    assert "cuda.is_available" in text or "torch.cuda.is_available" in text


def test_phase21_notebook_has_no_benchmark_or_mock_fallback() -> None:
    text = _notebook_text()
    for cmd in (
        "python scripts/run_full_benchmark",
        "python scripts/run_benchmark",
        "python scripts/run_calibration",
        "python scripts/run_judge",
        "python scripts/run_statistics",
        "python scripts/run_live_demo",
        "python scripts/build_index",
        "--allow-full-420",
    ):
        assert cmd not in text, cmd
    assert "falling back to mock" not in text.lower()
    assert "ollama_dev" not in text
    assert "backend_name = 'mock'" not in text
    assert "V2_LIVE_BACKEND'] = 'mock'" not in text
    assert "V2_LIVE_BACKEND'] = 'ollama" not in text
    assert "Do **not** open" in text or "not the Mac" in text
    assert "proxyPort(8501)" in text
