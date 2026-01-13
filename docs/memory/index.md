# Memory Module: Dynamic Token Window & Semantic Compression

This module manages the Agent's dialogue memory, specifically addressing common issues in long-document retrieval scenarios, such as context overflow and noise interference.

## 🌟 Key Features

### 1. Dynamic Token Window Management

Moving beyond unstable "fixed-turn" strategies, this module performs real-time actuarial calculations based on the model's Context Window:

* **Real-time Quota Monitoring:** Automatically calculates used tokens and remaining space before each dialogue turn.
* **Anchor Protection:** Force-anchors the `System Prompt` to ensure core instructions are never evicted from the context, even in extreme scenarios.

### 2. Tiered Retention Strategy

Asymmetric memory retention logic specifically designed for RAG scenarios:

* **Short-term (Full-Text):** Retains full raw text for only the most recent 2 turns to maintain immediate conversational tone and fluency.
* **Long-term (Summary):** Historical records prior to the last 2 turns automatically trigger **Summary Compression**, converting verbose dialogues into refined semantic cues.

### 3. Retrieval Trace Cleaning

Specialized processing for "dirty data" returned by tools:

* **Noise Filtering:** Automatically identifies and prunes raw debugging logs and redundant error messages (e.g., "Information not found") returned by tools.
* **Semantic Distillation:** De-duplicates retrieved Markdown fragments, feeding only the most essential knowledge points to the model to prevent context pollution.

---

## 🛠️ Memory Structure Example

The logic for constructing the processed context is as follows:

| Layer | Processing Method | Contents |
| --- | --- | --- |
| **System Layer** | **Permanent Retention** | Core persona settings, task instructions, and operational constraints. |
| **Long-term Memory** | **Semantic Summary** | Previous task objectives and confirmed factual conclusions. |
| **Short-term Memory** | **Full-Text** | Most recent user queries and detailed Agent responses. |
| **Tool Cache** | **Streamlined Injection** | Cleaned Markdown chunks and essential metadata paths. |
