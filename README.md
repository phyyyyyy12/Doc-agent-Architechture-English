# 🏢 Tech-Document-Agent Architecture

> A record of architectural evolution for enterprise-grade Tech-Doc Agents based on deep parsing.

## 🗺️ Architecture Navigation

| Core Components | 💡 Current Implementation (Status Quo) | 🔄 Architectural Evolution (ADR/Deep Dive) |
| --- | --- | --- |
| **1. Memory Management** | [Dynamic Token Window & Semantic Compression](./docs/memory/index.md) | [From "Keep Everything" to "Token Efficiency"](./docs/memory/evolution.md) |
| **2. Document Parser** | [Markdown Structure-Aware Intelligent Chunking](./docs/parser/index.md) | [From "Brute-Force Splitting" to "Structural Awareness"](./docs/parser/evolution.md) |

---

## 🎯 Core Value Propositions

1. **Structural Cognition**: Moving beyond simple RAG by identifying Markdown `#` header hierarchies to build deep knowledge indexes, ensuring context is never lost during retrieval.
2. **Traceable Decisions**: Utilizing an "Evolution Log" pattern to document how memory systems and token management are optimized, incorporating design philosophies from cutting-edge frameworks like Doubao Agent.
3. **Enterprise-Grade Implementation**: Specifically engineered to solve **Context Overflow** issues in long-document scenarios.

---

## 📂 Quick Access to Implementation (Source Code)

* `src/memory_manager.py`: Implementation of the dynamic token weight pruning algorithm.
* `src/md_parser.py`: Structured chunking logic based on header paths (Breadcrumbs).
