# Phase completion — backup reminder template

Copy this block into the master record phase section or phase completion report.  
**Do not claim backups exist unless paths are verified.**

---

## Phase N — [Name] — backup checkpoint

**Date:** YYYY-MM-DD

### Important files created/changed

- …

### Current storage location

| Item | Location | Verified? |
| --- | --- | --- |
| Source/config | Local V2 repo + GitHub | ☐ |
| Raw results | Drive `MSc-RAG/results/raw/` | ☐ NEEDS VERIFICATION |
| Checkpoints | Drive `MSc-RAG/checkpoints/` | ☐ NEEDS VERIFICATION |
| Logs | Drive `MSc-RAG/logs/` | ☐ NEEDS VERIFICATION |
| Large artefacts | Drive `MSc-RAG/artifacts/` | ☐ NEEDS VERIFICATION |

### Backup status (report only — not assumptions)

```text
Backup status:
* Colab: [ephemeral / synced to Drive / N/A for this phase]
* Google Drive: [path if verified, else NEEDS VERIFICATION]
* Local: [path if verified, else recommended]
* GitHub: [committed / uncommitted / recommended files list]

Action needed:
* [specific next steps for the user]
```

### Local backup recommendation

- [ ] Recommended after this phase: yes / no  
- Reason: …

### GitHub commit recommendation

- [ ] Recommended commit message: `Phase N: …`  
- Files to include: …  
- Files to exclude (large/raw): …

### Pre-destructive-operation checklist (if applicable)

- [ ] Latest checkpoint verified  
- [ ] Important files on Drive or local backup  
- [ ] Safe to proceed  

---

## Example (Phase 4 freeze — illustrative)

```text
Backup status:
* Colab: N/A (no Colab run)
* Google Drive: NEEDS VERIFICATION (manifest not yet copied to Drive)
* Local: verified — V2/data/final/selected_140_questions.csv
* GitHub: recommended — commit CSV + sampling_manifest.json

Action needed:
* Copy freeze files to Google Drive/MSc-RAG/configs/ if desired
* git add data/final/ && git commit -m "Phase 4: freeze 140 test questions"
```
