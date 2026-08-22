# Architecture Assets

This file describes all architecture diagrams used in the Enterprise AI Evaluation Dashboard.

The Home page should load the first diagram (Overall System Architecture) as the architecture preview.

The Architecture page should display every diagram in the order below.

---

# Diagram 1

File

system_architecture.png

Title

Overall System Architecture

Caption

Overall architecture of the proposed Multi-Agent Retrieval-Augmented Generation framework with Uncertainty Quantification. The framework begins with the RAGBench benchmark dataset, constructs a searchable knowledge base, evaluates three RAG architectures, and performs quantitative evaluation using RAGAS metrics, statistical analysis, confidence calibration and qualitative error analysis.

Short explanation

Shows the complete end-to-end research workflow.

------------------------------------------------------------

Flow

RAGBench Benchmark

↓

Knowledge Base Construction

↓

ChromaDB Vector Database

↓

Semantic Retrieval

↓

Single-Agent RAG

Multi-Agent RAG

Multi-Agent RAG + UQ

↓

420 Generated Responses

↓

1680 RAGAS Evaluations

↓

Research Analysis

↓

Final Results

------------------------------------------------------------

# Diagram 2

File

knowledge_base.png

Title

Knowledge Base Construction

Caption

Knowledge base creation pipeline used to transform enterprise documents into a searchable vector database.

Short explanation

Enterprise documents are parsed, cleaned, semantically chunked, embedded using Sentence Transformers and indexed in ChromaDB.

------------------------------------------------------------

Flow

Enterprise Documents

↓

Document Parsing

↓

Text Cleaning

↓

Semantic Chunking

↓

Embedding Generation

↓

ChromaDB Vector Store

↓

Enterprise Knowledge Base

------------------------------------------------------------

# Diagram 3

File

single_agent_rag.png

Title

Baseline Single-Agent RAG

Caption

Traditional Retrieval-Augmented Generation pipeline used as the baseline architecture.

Short explanation

A semantic retriever retrieves the most relevant document chunks which are combined with the user question before generating a response.

------------------------------------------------------------

Flow

User Question

↓

Semantic Retriever

↓

Top-k Retrieval

↓

Context Assembly

↓

Qwen 3 8B (Ollama)

↓

Generated Answer

------------------------------------------------------------

# Diagram 4

File

multi_agent_uq.png

Title

Proposed Multi-Agent RAG with Uncertainty Quantification

Caption

Proposed multi-agent architecture incorporating retrieval, verification, reasoning and confidence estimation before generating the final response.

Short explanation

Multiple specialised agents collaboratively retrieve, validate and reason over evidence before estimating confidence and selecting the final system response.

------------------------------------------------------------

Flow

User Question

↓

Semantic Retrieval

↓

Retrieved Documents

↓

Retrieval Agent

↓

Verification Agent

↓

Reasoning Agent

↓

Confidence Estimation

↓

Decision Threshold

↓

High Confidence → Answer

Medium Confidence → Answer + Warning

Low Confidence → Abstain

------------------------------------------------------------

# Diagram 5

File

project_lifecycle.png

Title

End-to-End Development and Evaluation Lifecycle

Caption

Complete lifecycle of the MSc research project from benchmark selection through evaluation, statistical validation and dissertation preparation.

Short explanation

Illustrates the complete research methodology implemented during the project.

------------------------------------------------------------

Flow

RAGBench Dataset

↓

Knowledge Base

↓

Semantic Retrieval

↓

Three RAG Systems

↓

420 Generated Responses

↓

1680 RAGAS Evaluations

↓

Statistical Validation

↓

Confidence Calibration

↓

Publication Figures

↓

Qualitative Error Analysis

↓

Dissertation

------------------------------------------------------------

Dashboard Behaviour

The Home page should display only Diagram 1.

The Architecture page should display all five diagrams.

Each diagram should be presented inside an expandable card.

Each card should contain

• Diagram title

• Image

• One-sentence explanation

• Caption underneath

Clicking the image should enlarge it.

Use consistent sizing for every diagram.

Do not display multiple diagrams on the Home page.
