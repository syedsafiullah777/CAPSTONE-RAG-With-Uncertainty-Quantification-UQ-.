"""Read-only consistency checks for the frozen research chain."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from src.audit import verify_audit_does_not_import_generation
from src.calibration.lock import EXPECTED_LOCKED_THRESHOLD, load_official_lock
from src.config import project_root
from src.statistics.constants import (
    ARCHITECTURES,
    CAL_40_REL,
    EXPECTED_CAL40_SHA256,
    EXPECTED_FROZEN140_SHA256,
    EXPECTED_JUDGE_SHA256,
    EXPECTED_LOCK_SHA256,
    EXPECTED_PHASE15_SHA256,
    EXPECTED_PROCESSED_SHA256,
    FROZEN_140_REL,
    JUDGE_METRIC_LABEL,
    JUDGE_REL,
    LOCKED_T,
    LOCK_REL,
    PHASE15_REL,
    PROCESSED_REL,
)
from src.statistics.load import sha256_file, verify_frozen_hashes
from src.run.subset import ids_sha256

PASS = "PASS"
FAIL = "FAIL"
NV = "NEEDS VERIFICATION"

FIGURE_STEMS = (
    "rq1_answer_correctness_95ci",
    "rq2_confidence_vs_faithfulness",
    "rq3_coverage_vs_selective_accuracy",
    "rq1_mcnemar_counts",
    "rq2_faithfulness_distribution",
    "rq3_uq_outcomes",
)


def _check(name: str, status: str, detail: str) -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _git(root: Path, *args: str) -> str:
    repo = root.parent
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return (result.stdout or "") + (result.stderr or "")


def run_audit(root: Path | None = None) -> dict[str, Any]:
    verify_audit_does_not_import_generation()
    root = root or project_root()
    checks: list[dict[str, str]] = []

    try:
        hashes = verify_frozen_hashes(root)
        checks.append(_check(
            "frozen_artefact_sha256",
            PASS,
            "Phase 15/16/140/40/lock SHA-256 match src/statistics/constants.py: "
            + ", ".join(f"{k}={v[:12]}…" for k, v in hashes.items()),
        ))
    except Exception as exc:
        hashes = {}
        checks.append(_check("frozen_artefact_sha256", FAIL, str(exc)))

    lock = load_official_lock()
    t_ok = abs(float(lock["threshold"]) - EXPECTED_LOCKED_THRESHOLD) < 1e-9
    checks.append(_check(
        "locked_threshold",
        PASS if t_ok and lock.get("locked") and lock.get("source_split") == "dev" and not lock.get("used_frozen_test_140") else FAIL,
        f"T={lock.get('threshold')} locked={lock.get('locked')} source_split={lock.get('source_split')} "
        f"used_frozen_test_140={lock.get('used_frozen_test_140')} n={lock.get('n')} "
        f"rule={lock.get('rule')} coverage={lock.get('coverage')} selective={lock.get('selective_accuracy')}",
    ))

    frozen = _csv_rows(root / FROZEN_140_REL)
    cal = _csv_rows(root / CAL_40_REL)
    frozen_ids = [row["id"] for row in frozen]
    cal_ids = [row["id"] for row in cal]
    freeze_ok = (
        len(frozen_ids) == 140
        and len(set(frozen_ids)) == 140
        and all(row.get("split") == "test" for row in frozen)
        and len(cal_ids) == 40
        and len(set(cal_ids)) == 40
        and all(row.get("split") == "dev" for row in cal)
        and not (set(frozen_ids) & set(cal_ids))
    )
    lock_ids = list(lock.get("question_ids") or [])
    cal_lock_ok = set(cal_ids) == set(lock_ids) and len(lock_ids) == 40
    checks.append(_check(
        "frozen_140_and_dev_40",
        PASS if freeze_ok and cal_lock_ok else FAIL,
        f"n_test={len(frozen_ids)} unique_test={len(set(frozen_ids))} n_dev={len(cal_ids)} "
        f"overlap_test_dev={len(set(frozen_ids)&set(cal_ids))} lock_ids_match_cal40={cal_lock_ok}",
    ))

    p15 = _jsonl(root / PHASE15_REL)
    p16 = _jsonl(root / PROCESSED_REL)
    judge = _jsonl(root / JUDGE_REL)
    keys15 = [str(r["case_key"]) for r in p15]
    keys16 = [str(r["case_key"]) for r in p16]
    keys_j = [str(r["case_key"]) for r in judge]
    arches15 = Counter(str(r["architecture"]) for r in p15)
    q15 = {str(r["question_id"]) for r in p15}
    complete = (
        len(p15) == 420 and len(set(keys15)) == 420
        and len(p16) == 420 and set(keys16) == set(keys15)
        and len(judge) == 420 and set(keys_j) == set(keys15)
        and all(arches15[a] == 140 for a in ARCHITECTURES)
        and q15 == set(frozen_ids)
    )
    uq15 = [r for r in p15 if r.get("architecture") == "multi_agent_uq"]
    uq_t = all(abs(float(r.get("threshold") or 0) - LOCKED_T) < 1e-9 for r in uq15)
    uq_dec = Counter(str(r.get("decision")) for r in uq15)
    judge_rerun = any(bool(r.get("used_rag_rerun")) for r in judge)
    judge_fail = sum(
        1
        for r in judge
        if r.get("parse_failure")
        or r.get("error")
        or str(r.get("case_status") or "").upper() != "COMPLETED"
    )
    judge_settings = all(
        abs(float(r.get("temperature") if r.get("temperature") is not None else -1) - 0.0) < 1e-9
        and int(r.get("max_new_tokens") or 0) == 32
        and int(r.get("n_ctx") or 0) == 4096
        for r in judge
    )
    checks.append(_check(
        "benchmark_420_completeness",
        PASS if complete and uq_t and not judge_rerun and judge_fail == 0 else FAIL,
        f"phase15={len(p15)} unique={len(set(keys15))} per_arch={dict(arches15)} "
        f"ids_match_freeze={q15==set(frozen_ids)} processed_keys_match={set(keys16)==set(keys15)} "
        f"judge_keys_match={set(keys_j)==set(keys15)} uq_threshold_all_0.65={uq_t} "
        f"uq_decisions={dict(uq_dec)} judge_used_rag_rerun={judge_rerun} "
        f"judge_noncomplete_or_parse_fail={judge_fail} "
        f"judge_call_settings_jsonl_T0_32tok_nctx4096={judge_settings}",
    ))

    desc = {row["architecture"]: row for row in _csv_rows(root / "results/metrics/phase17_descriptive.csv")}
    p16_sum = {row["architecture"]: row for row in _csv_rows(root / "results/metrics/phase16_summary.csv")}
    k_match = (
        int(float(desc["single_agent"]["displayed_correct_k"])) == 32
        and int(float(desc["multi_agent"]["displayed_correct_k"])) == 29
        and int(float(desc["multi_agent_uq"]["displayed_correct_k"])) == 32
        and int(float(desc["multi_agent_uq"]["n_answer"])) == 78
        and int(float(desc["multi_agent_uq"]["n_abstain"])) == 62
        and int(float(p16_sum["single_agent"]["n_correct_displayed"])) == 32
        and int(float(p16_sum["multi_agent"]["n_correct_displayed"])) == 29
        and int(float(p16_sum["multi_agent_uq"]["n_correct_displayed"])) == 32
        and int(float(p16_sum["multi_agent_uq"]["n_correct_claim"])) == 34
    )
    checks.append(_check(
        "phase16_phase17_count_traceability",
        PASS if k_match else FAIL,
        "Displayed correct SA/MA/UQ = 32/29/32; UQ ANSWER/ABSTAIN = 78/62; UQ claim correct = 34. "
        "Phase 16 summary CSV matches Phase 17 descriptive CSV on these counts.",
    ))

    tests = {row["id"]: row for row in _csv_rows(root / "results/metrics/phase17_tests.csv")}
    rq1 = tests["rq1_mcnemar_displayed_sa_vs_ma"]
    spear = tests["rq2_spearman_uq_confidence_vs_llm_faithfulness"]
    stats_ok = (
        abs(float(rq1["p_value"]) - 0.6776) < 5e-4
        and int(float(rq1["n11_both_positive"])) == 19
        and int(float(rq1["n10_left_only"])) == 13
        and int(float(rq1["n01_right_only"])) == 10
        and int(float(rq1["n00_both_negative"])) == 98
        and abs(float(spear["statistic"]) - 0.6988) < 5e-5
        and spear.get("layer", "").startswith("LLM-as-judge faithfulness")
        and "official RAGAS" not in spear.get("layer", "")
    )
    checks.append(_check(
        "phase17_statistics_traceability",
        PASS if stats_ok else FAIL,
        f"McNemar SA vs MA p={rq1['p_value']} cells=19/13/10/98 Holm={rq1['p_value_holm']} "
        f"sig={rq1['significant_holm_0.05']}; Spearman rho={spear['statistic']} "
        f"layer={spear.get('layer')}",
    ))

    fig_index = (root / "results/metrics/phase17_figures/FIGURE_INDEX.md").read_text(encoding="utf-8")
    fig_table_ok = (
        "32/140 = 22.86%" in fig_index
        and "29/140 = 20.71%" in fig_index
        and "Spearman ρ = 0.6988" in fig_index
        and "78/140 = 55.71%" in fig_index
        and "32/78 = 41.03%" in fig_index
        and "both correct 19" in fig_index
        and "Single-Agent only 13" in fig_index
        and "Multi-Agent only 10" in fig_index
        and "both incorrect 98" in fig_index
        and "ANSWER correct 32" in fig_index
        and "ANSWER incorrect 46" in fig_index
        and "ABSTAIN incorrect draft 60" in fig_index
        and "ABSTAIN correct draft 2" in fig_index
        and abs(float(desc["single_agent"]["displayed_correctness"]) - 0.2286) < 5e-4
        and abs(float(desc["multi_agent"]["displayed_correctness"]) - 0.2071) < 5e-4
        and abs(float(desc["multi_agent_uq"]["coverage"]) - 0.5571) < 5e-4
        and abs(float(desc["multi_agent_uq"]["selective_accuracy"]) - 0.4103) < 5e-4
        and abs(float(desc["single_agent"]["llm_faithfulness_mean"]) - 0.3241) < 5e-4
        and abs(float(desc["multi_agent"]["llm_faithfulness_mean"]) - 0.3484) < 5e-4
        and abs(float(desc["multi_agent_uq"]["llm_faithfulness_mean"]) - 0.3749) < 5e-4
    )
    checks.append(_check(
        "figure_to_table_consistency",
        PASS if fig_table_ok else FAIL,
        "FIGURE_INDEX counts match Phase 17 descriptive/tests CSVs "
        "(SA/MA/UQ displayed 32/29/32; McNemar 19/13/10/98; Spearman 0.6988; "
        "coverage 78/140; selective 32/78; UQ outcomes 32/46/60/2; "
        "judge means 0.3241/0.3484/0.3749).",
    ))

    summary_json = json.loads(
        (root / "results/config/phase17_statistics_summary.json").read_text(encoding="utf-8")
    )
    outcomes = summary_json.get("rq3_abstention_outcomes")
    interp = str((summary_json.get("interpretation") or {}).get("rq3") or "")
    outcomes_in_text = (
        "true abstain (incorrect draft) 60" in interp
        and "false abstain (correct draft withheld) 2" in interp
    )
    if outcomes is None:
        outcome_status = NV
        outcome_detail = (
            "FIGURE_INDEX cites results/config/phase17_statistics_summary.json key "
            "`rq3_abstention_outcomes`, but that key is absent from the saved JSON. "
            f"Interpretation text has 60/2={outcomes_in_text}. Do not rewrite the JSON."
        )
    elif (
        int(outcomes.get("true_positive_answer_displayed_correct") or -1) == 32
        and int(outcomes.get("false_positive_answer_displayed_incorrect") or -1) == 46
        and int(outcomes.get("true_abstain_incorrect_draft") or -1) == 60
        and int(outcomes.get("false_abstain_correct_draft") or -1) == 2
        and abs(float(outcomes.get("threshold") or 0) - LOCKED_T) < 1e-9
        and outcomes_in_text
    ):
        outcome_status = PASS
        outcome_detail = (
            "phase17_statistics_summary.json `rq3_abstention_outcomes` is present and matches "
            "FIGURE_INDEX / Phase 18: ANSWER correct 32, ANSWER incorrect 46, "
            "ABSTAIN incorrect draft 60, ABSTAIN correct draft 2, T=0.65."
        )
    else:
        outcome_status = NV
        outcome_detail = (
            f"rq3_abstention_outcomes present but counts unexpected: {outcomes}. "
            f"interpretation_has_60_and_2={outcomes_in_text}. Not rewritten."
        )
    checks.append(_check(
        "phase17_json_rq3_abstention_outcomes_key",
        outcome_status,
        outcome_detail,
    ))

    render_meta = json.loads(
        (root / "results/config/phase17_figure_render.json").read_text(encoding="utf-8")
    )
    pinned = render_meta.get("result_file_sha256") or {}
    drift = []
    for rel, expected in pinned.items():
        path = root / rel
        if not path.is_file():
            drift.append(f"{rel}: missing")
            continue
        digest = sha256_file(path)
        if digest != expected:
            drift.append(f"{rel}: {digest} != {expected}")
    checks.append(_check(
        "no_accidental_phase17_result_changes",
        PASS if not drift else FAIL,
        "Phase 17 table/JSON SHA-256 still match phase17_figure_render.json pins."
        if not drift
        else f"SHA drift vs figure-render pins: {drift}",
    ))

    fp = json.loads(
        (root / "results/config/phase16_judge_runtime_fingerprint.json").read_text(encoding="utf-8")
    )
    mc = fp.get("model_config") or {}
    checks.append(_check(
        "judge_fingerprint_vs_jsonl_settings",
        NV,
        "Judge JSONL is the source of truth for judge-call settings "
        f"(observed temperature=0.0, max_new_tokens=32, n_ctx=4096, all_match={judge_settings}). "
        f"phase16_judge_runtime_fingerprint.json model_config has temperature={mc.get('temperature')} "
        f"max_new_tokens={mc.get('max_new_tokens')} (RAG generation defaults). "
        "Documented in Phase 16 judge notes; not treated as a result rewrite.",
    ))

    samp = json.loads((root / "data/final/sampling_manifest.json").read_text(encoding="utf-8"))
    calm = json.loads((root / "data/calibration/calibration_manifest.json").read_text(encoding="utf-8"))
    samp_ids = list(samp.get("selected_ids") or [])
    calm_ids = list(calm.get("selected_ids") or [])
    lock_join_sha = ids_sha256(lock_ids)
    id_sets_ok = (
        set(samp_ids) == set(frozen_ids)
        and samp.get("selected_ids_sha256")
        and set(calm_ids) == set(cal_ids)
        and set(lock_ids) == set(cal_ids)
        and lock.get("question_ids_sha256") == lock_join_sha
    )
    hash_convention_note = (
        f"sampling_manifest.selected_ids_sha256={samp.get('selected_ids_sha256')} "
        f"(JSON array fingerprint); lock.question_ids_sha256={lock.get('question_ids_sha256')} "
        f"(newline-joined ids_sha256); calibration_manifest.selected_ids_sha256="
        f"{calm.get('selected_ids_sha256')}. Different hash conventions; ID sets match CSVs."
    )
    checks.append(_check(
        "manifest_id_sets_vs_csv",
        PASS if id_sets_ok else FAIL,
        hash_convention_note + f" id_sets_ok={id_sets_ok}",
    ))

    fig_dir = root / "results/metrics/phase17_figures"
    fig_files = sorted(p.name for p in fig_dir.iterdir() if p.is_file()) if fig_dir.is_dir() else []
    expected_figs = [f"{s}{ext}" for s in FIGURE_STEMS for ext in (".png", ".pdf")]
    extra = [n for n in fig_files if n not in expected_figs and n != "FIGURE_INDEX.md"]
    missing = [n for n in expected_figs if n not in fig_files]
    dirty = any(tok in n.lower() for n in fig_files for tok in ("_1.", "final", "new.", "copy", "revised"))
    svg = [n for n in fig_files if n.endswith(".svg")]
    fig_ok = not missing and not extra and not dirty and not svg
    checks.append(_check(
        "phase17_figures_canonical_set",
        PASS if fig_ok else FAIL,
        f"files={fig_files} missing={missing} extra={extra} svg={svg}",
    ))

    p18_cases = _csv_rows(root / "results/analysis/phase18_error_cases.csv")
    p18_sum = _csv_rows(root / "results/analysis/phase18_error_summary.csv")
    by_arch_cat = {(r["architecture"], r["primary_category"]): int(r["n"]) for r in p18_sum}
    p18_ok = (
        len(p18_cases) == 420
        and by_arch_cat.get(("multi_agent_uq", "incorrect_abstention"), -1) == 2
        and by_arch_cat.get(("multi_agent_uq", "appropriate_abstention"), -1) == 60
        and by_arch_cat.get(("single_agent", "correct_answer"), -1) == 32
        and by_arch_cat.get(("multi_agent", "correct_answer"), -1) == 29
        and by_arch_cat.get(("multi_agent_uq", "correct_answer"), -1) == 32
        and sum(int(r["n"]) for r in p18_sum if r["architecture"] == "single_agent") == 140
        and sum(1 for r in p18_cases if str(r.get("in_qualitative_sample")).lower() == "true") == 81
        and by_arch_cat.get(("single_agent", "unsupported_claim"), -1) == 55
        and by_arch_cat.get(("multi_agent", "unsupported_claim"), -1) == 52
        and by_arch_cat.get(("multi_agent_uq", "unsupported_claim"), -1) == 10
        and by_arch_cat.get(("single_agent", "retrieval_failure"), -1) == 13
        and by_arch_cat.get(("multi_agent", "retrieval_failure"), -1) == 13
    )
    n_sample = sum(1 for r in p18_cases if str(r.get("in_qualitative_sample")).lower() == "true")
    checks.append(_check(
        "phase18_error_analysis_consistency",
        PASS if p18_ok else FAIL,
        f"n_cases={len(p18_cases)} sample={n_sample} "
        f"UQ false_abstain={by_arch_cat.get(('multi_agent_uq','incorrect_abstention'))} "
        f"UQ true_abstain={by_arch_cat.get(('multi_agent_uq','appropriate_abstention'))} "
        f"unsupported_claim SA/MA/UQ="
        f"{by_arch_cat.get(('single_agent','unsupported_claim'))}/"
        f"{by_arch_cat.get(('multi_agent','unsupported_claim'))}/"
        f"{by_arch_cat.get(('multi_agent_uq','unsupported_claim'))}",
    ))

    yaml_text = (root / "config/experiment.yaml").read_text(encoding="utf-8")
    yaml_stale = "phase5_threshold_locked: false" in yaml_text
    checks.append(_check(
        "experiment_yaml_threshold_fields",
        NV if yaml_stale else PASS,
        "Official T is threshold.lock.json; yaml confidence_threshold is null by design (Phase 12 isolation). "
        "dataset.phase5_threshold_locked remains false as a leftover Phase 5 freeze flag — stale relative to Phase 13 lock; "
        "not treated as the scientific source of T.",
    ))

    metric_ok = JUDGE_METRIC_LABEL in (root / "results/final/phase17_interpretation.md").read_text(encoding="utf-8")
    checks.append(_check(
        "metric_definitions",
        PASS if metric_ok else FAIL,
        f"Primary RQ2 label is `{JUDGE_METRIC_LABEL}` — not official RAGAS. "
        "RQ1 = displayed numeric FinQA match. RQ3 = coverage/selective accuracy/unsupported_emitted at locked T. "
        "unsupported_emitted = ANSWER and displayed numeric incorrect (not a hallucination label).",
    ))

    tracked_jsonl = _git(root, "ls-files")
    tracked = [
        line.strip()
        for line in tracked_jsonl.splitlines()
        if line.strip().endswith(".jsonl")
    ]
    large_raw = [p for p in tracked if "phase15_benchmark" in p and p.endswith("cases.jsonl")]
    large_judge = [p for p in tracked if "phase16_judge" in p and p.endswith("judge.jsonl")]
    checks.append(_check(
        "git_does_not_track_raw_jsonl_dumps",
        PASS if not large_raw and not large_judge else FAIL,
        f"tracked jsonl count={len(tracked)}; forbidden_raw={large_raw}; forbidden_judge={large_judge}; "
        f"tracked={tracked[:20]}",
    ))

    drive_hits: list[str] = []
    home = Path.home()
    for base in [home / "Google Drive", home / "My Drive", *home.glob("Library/CloudStorage/GoogleDrive-*")]:
        for suffix in (
            "MSc-RAG",
            "My Drive/MSc-RAG",
            "MyDrive/MSc-RAG",
        ):
            cand = base / suffix if suffix != "MSc-RAG" else base / "MSc-RAG"
            if cand.is_dir():
                drive_hits.append(str(cand))
        if (base / "MSc-RAG").is_dir():
            drive_hits.append(str(base / "MSc-RAG"))
    checks.append(_check(
        "google_drive_archive",
        NV,
        "No Google Drive MSc-RAG folder was listed from this Mac. "
        f"Searched CloudStorage/GoogleDrive, ~/Google Drive, ~/My Drive. hits={drive_hits or 'none'}. "
        "Do not claim a Drive backup exists.",
    ))

    gh = _git(root, "remote", "-v")
    status = _git(root, "status", "--short", "V2")
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    checks.append(_check(
        "github_status",
        NV,
        f"branch={branch}. Remote:\n{gh.strip() or '(none)'}\nWorking tree (short, may include uncommitted V2 work):\n"
        f"{status.strip() or '(clean in captured snapshot)'}. "
        "Phase 15–18 research code/docs were not required to be committed by this audit.",
    ))

    local_required = [
        root / PHASE15_REL,
        root / PROCESSED_REL,
        root / JUDGE_REL,
        root / FROZEN_140_REL,
        root / CAL_40_REL,
        root / LOCK_REL,
        root / "results/metrics/phase17_tests.csv",
        root / "results/analysis/phase18_error_cases.csv",
        root / "results/final/phase18_error_analysis.md",
    ]
    missing_local = [str(p.relative_to(root)) for p in local_required if not p.is_file()]
    checks.append(_check(
        "required_local_artefacts",
        PASS if not missing_local else FAIL,
        "All required local chain files are present." if not missing_local else f"missing={missing_local}",
    ))

    master = (root / "project_record/PROJECT_MASTER_RECORD.md").read_text(encoding="utf-8")
    plan = (root / "docs/IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
    ctx = (root / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    chrono_notes = []
    if "Phase 18 complete" not in master and "## Phase 18" not in master:
        chrono_notes.append("master record missing Phase 18 section")
    if "Next phase (not started)" in master and "Phase 19" in master.split("Next phase (not started)")[1][:80]:
        chrono_notes.append("master header still lists Phase 19 as next (expected until this audit is recorded)")
    if "Phase 19 dissertation evidence pack" in plan and "Phase 18 complete" in plan:
        chrono_notes.append("implementation plan still names Phase 19 as next (stale after this audit is recorded)")
    if "Phase 19 dissertation evidence pack not started" in ctx:
        chrono_notes.append("PROJECT_CONTEXT still says Phase 19 not started")
    checks.append(_check(
        "documentation_chronology_pre_audit_write",
        NV if chrono_notes else PASS,
        "Historical Phase 15–18 remaining-issues lines that say a later phase was not started are dated history and were not rewritten. "
        "Current headers before this audit: " + ("; ".join(chrono_notes) or "headers already mention Phase 19 complete."),
    ))

    raw_status = _git(root, "status", "--short")
    non_v2 = [
        ln for ln in raw_status.splitlines()
        if len(ln) > 3
        and not ln[3:].startswith("V2/")
        and not ln[3:].lstrip().startswith(".")
    ]
    checks.append(_check(
        "v1_unmodified_in_this_audit",
        PASS if not non_v2 else NV,
        "Phase 19 audit writes only under V2/. V1 is reference-only. "
        f"Non-V2 status lines={non_v2[:8] or 'none'}",
    ))

    fail_n = sum(1 for c in checks if c["status"] == FAIL)
    nv_n = sum(1 for c in checks if c["status"] == NV)
    chain_names = {
        "frozen_artefact_sha256", "locked_threshold", "frozen_140_and_dev_40",
        "benchmark_420_completeness", "phase16_phase17_count_traceability",
        "phase17_statistics_traceability", "phase17_figures_canonical_set",
        "figure_to_table_consistency", "phase18_error_analysis_consistency",
        "metric_definitions", "git_does_not_track_raw_jsonl_dumps",
        "required_local_artefacts", "no_accidental_phase17_result_changes",
        "manifest_id_sets_vs_csv",
    }
    chain_fail = [c for c in checks if c["name"] in chain_names and c["status"] == FAIL]
    overall = FAIL if chain_fail else PASS

    return {
        "phase": 19,
        "overall": overall,
        "used_rag_rerun": False,
        "used_llm_inference": False,
        "recomputed_statistics": False,
        "hashes": hashes,
        "expected_hashes": {
            "phase15": EXPECTED_PHASE15_SHA256,
            "processed": EXPECTED_PROCESSED_SHA256,
            "judge": EXPECTED_JUDGE_SHA256,
            "frozen140": EXPECTED_FROZEN140_SHA256,
            "cal40": EXPECTED_CAL40_SHA256,
            "lock": EXPECTED_LOCK_SHA256,
        },
        "checks": checks,
        "chain_fail": [c["name"] for c in chain_fail],
        "n_pass": sum(1 for c in checks if c["status"] == PASS),
        "n_fail": fail_n,
        "n_needs_verification": nv_n,
        "locked_t": LOCKED_T,
        "judge_metric_label": JUDGE_METRIC_LABEL,
    }
