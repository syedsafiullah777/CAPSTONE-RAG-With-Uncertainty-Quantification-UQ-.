# Multi-Agent RAG Evaluation Platform

MSc final project prototype for:

**Design and Evaluation of a Multi-Agent Retrieval-Augmented Generation Framework with Uncertainty Quantification for Enterprise Knowledge Systems**

The project separates the **interactive Streamlit app** from the **automated research pipeline**. Both use the same backend retrieval, agent, uncertainty, and Ollama components.

## Architecture

```text
RAGBench / enterprise PDFs
        |
        v
Knowledge base: chunking -> embeddings -> ChromaDB
        |
        +--> evaluation pipeline -> experiment_results.csv -> summary.csv -> charts
        |
        +--> Streamlit app -> live question answering + dashboard
```

## Project Structure

```text
app/
  streamlit_app.py
  pages/
    Chat.py
    Dashboard.py
    About.py

data/
  ragbench/
  sampled_questions.csv

knowledge_base/
  documents/
  embeddings/

models/
  ollama.py

rag/
  retriever.py
  embeddings.py
  chunking.py
  single_agent.py
  multi_agent.py
  uncertainty.py

evaluation/
  dataset_loader.py
  evaluator.py
  metrics.py
  experiment.py
  save_results.py
  charts.py

results/
  experiment_results.csv
  summary.csv
  charts/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install or start Ollama, then make sure the configured model exists:

```bash
ollama pull qwen3.5:9b
```

If your model name differs, edit `OLLAMA_MODEL` in `config.py`.

## Run The Streamlit App

```bash
streamlit run app.py
```

The app is for interactive demonstration:

1. Upload PDFs.
2. Build the shared knowledge base.
3. Ask a question.
4. Compare Single-Agent RAG, Multi-Agent RAG, and Multi-Agent RAG + UQ.

The Dashboard page reads saved research outputs from `results/`; it does not rerun the benchmark.

## RAGBench Sampling

Create a reproducible 300-question sample:

```bash
python -m evaluation.dataset_loader
```

The sample plan is defined in `config.py`:

| Dataset | Questions |
| --- | ---: |
| techqa | 100 |
| emanual | 100 |
| cuad | 50 |
| finqa | 25 |
| expertqa | 25 |

The output is:

```text
data/sampled_questions.csv
```

## Run The Automated Experiment

Build the shared knowledge base from the sampled RAGBench contexts:

```bash
python -m evaluation.build_knowledge_base
```

Then run the experiment:

```bash
python -m evaluation.experiment
```

This runs every sampled question through:

- Single-Agent RAG
- Multi-Agent RAG
- Multi-Agent RAG + Uncertainty Quantification

Outputs:

```text
results/experiment_results.csv
results/summary.csv
```

## Generate Dissertation Charts

```bash
python -m evaluation.charts
```

Outputs:

```text
results/charts/accuracy.png
results/charts/hallucination.png
results/charts/confidence.png
results/charts/response_time.png
```

## Research Design

The comparison is controlled:

- Same documents
- Same embedding model
- Same ChromaDB index
- Same Ollama/Qwen model
- Same benchmark questions

Only the workflow changes:

| System | Workflow |
| --- | --- |
| Single-Agent RAG | Retriever -> LLM |
| Multi-Agent RAG | Retriever -> LLM -> Verifier |
| Multi-Agent RAG + UQ | Retriever -> LLM -> Verifier -> Uncertainty -> Decision |

Core metrics:

- Answer correctness
- Faithfulness
- Retrieval precision
- Hallucination rate
- Mean confidence
- Abstention rate
- Average response time
