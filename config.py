from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAGBENCH_DIR = DATA_DIR / "ragbench"
SAMPLED_QUESTIONS_PATH = DATA_DIR / "sampled_questions.csv"

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
PDF_DIR = KNOWLEDGE_BASE_DIR / "documents"
EMBEDDINGS_DIR = KNOWLEDGE_BASE_DIR / "embeddings"
BENCHMARK_DIR = DATA_DIR / "benchmark"
VECTORSTORE_DIR = EMBEDDINGS_DIR / "chroma"
RESULTS_DIR = PROJECT_ROOT / "results"
CHARTS_DIR = RESULTS_DIR / "charts"

COLLECTION_NAME = "enterprise_policies"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
OLLAMA_MODEL = "qwen3.5:9b"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 4

ANSWER_THRESHOLD = 0.80
WARNING_THRESHOLD = 0.50

RANDOM_SEED = 42
RAGBENCH_SAMPLE_PLAN = {
    "techqa": 100,
    "emanual": 100,
    "cuad": 50,
    "finqa": 25,
    "expertqa": 25,
}
