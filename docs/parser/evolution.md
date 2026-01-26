## 🛠 Evolution & Insights

> "The success of RAG is determined by data cleaning. Every extra effort spent on parsing saves ten times the effort during retrieval."

### 📅 Project Milestones

#### **v2.0 - Structure-Aware Parser (Current)** ``

* **Core Philosophy:** Moving away from "brute-force splitting" toward "deep syntactic parsing."
* **Key Improvements:**
* **Intelligent Boundaries:** Introduced `Boundary Protection` with strict validation for Code Blocks and Tables, strictly prohibiting cross-line splitting.
* **Semantic Injection:** Implemented the `Breadcrumb` strategy, where each chunk automatically inherits its parent context path.
* **Field Standardization:** Unified metadata format (including `source_file`, `breadcrumb`, `heading_level`, etc.) to support precision Metadata Filtering.


* **Strategic Focus:** Explicitly focused on the Markdown ecosystem, deprecating complex RST support to pursue maximum parsing speed and accuracy.

#### **v1.0 - Basic Chunking Scheme** ``

* **Approach:** Fixed-size Character Chunking.
* **Pain Points:** Suffered from severe semantic fragmentation and loss of context, leading to poor Agent performance in code explanation scenarios.

---

## ⚖️ Architecture Comparison

| Feature | v1.0 Brute-Force Splitting | v2.0 Structure-Aware (Current) |
| --- | --- | --- |
| **Criteria** | Fixed character count | **Markdown Heading Hierarchy (# to ###)** |
| **Code Integrity** | Frequently truncated | **Regex Protection; internal splitting prohibited** |
| **Semantic Context** | None | **Breadcrumb (File > Parent Header > Sub-header)** |
| **Metadata** | Filename only | **Rich multi-dimensional tags (Heading/Level/Format)** |
| **Retrieval Quality** | Prone to drifting off-topic | **Precise localization of semantic background** |

---

## 🔮 Roadmap & Future Challenges

* [ ] **Multimodal Enhancement:** Semantic extraction for **Mermaid** diagrams embedded within Markdown.
* [ ] **Complex Formulas:** Optimize block boundary protection for **LaTeX** equations.
* [ ] **Dynamic Thresholds:** Automatically adjust `max_tokens` based on content complexity.

Would you like me to draft a sample **JSON Metadata Schema** for your v2.0 parser?
