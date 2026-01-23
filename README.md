# 🏢 Doc-Agent Architecture

> Enterprise-grade RAG Agent architecture evolved for deep Markdown document analysis.

## 🗺️ Architecture Navigation

| Core Component | 💡 Status Quo | 🔄 ADR / Evolution Deep Dive |
| --- | --- | --- |
| **1. Memory Management** | [Dynamic Token Window & Semantic Compression](https://www.google.com/search?q=./docs/memory/index.md) | [From "Keep All" to "Token Pruning"](https://www.google.com/search?q=./docs/memory/evolution.md) |
| **2. Document Parsing** | [Structure-Aware Markdown Chunking](https://www.google.com/search?q=./docs/parser/index.md) | [From "Fixed-Size" to "Structure-Aware"](https://www.google.com/search?q=./docs/parser/evolution.md) |
| **3. Reasoning Engine** | [Multi-modal ReAct Engine & Hybrid Planning](https://www.google.com/search?q=./docs/react/index.md) | [From "General Search" to "High-Precision Loop"](https://www.google.com/search?q=./docs/react/evolution.md) |

---

## 🎯 Core Implementation

| Module | Key Features | Source Code |
| --- | --- | --- |
| **ReAct Engine** | **Reasoning Loop**: Thought-Action-Observation cycle with auto-parsing and streaming termination. | [`react_core.py`](https://www.google.com/search?q=./react_core.py) |
| **Dynamic Memory** | **Token Calculus**: Real-time windowing with **System Anchor Protection** and **Far-field Semantic Compression**. | [`memory_core.py`](https://www.google.com/search?q=./memory_core.py) |
| **Structure-Aware Chunker** | **Syntax Sensitivity**: Hierarchy-based splitting with **Breadcrumb Path Inheritance** and code block protection. | [`chunker_core.py`](https://www.google.com/search?q=./chunker_core.py) |
| **Task Executor** | **Secure Orchestration**: Hybrid planning (Keyword + LLM) with RBAC tool checks and fault-tolerant retries. | [`executor_core.py`](https://www.google.com/search?q=./executor_core.py) |

---

### 🌟 Key Highlights

* **Intelligent Context**: The dynamic Token window strategy maintains near-field conversational fluency while preventing context overflow via far-field semantic summarization.
* **Semantic Integrity**: Structure-aware chunking prevents code/table truncation and injects full breadcrumb paths into every chunk for global context awareness.
* **Reliable Reasoning**: The ReAct loop combined with an execution sandbox minimizes hallucinations and ensures secure, transparent tool orchestration.

---
