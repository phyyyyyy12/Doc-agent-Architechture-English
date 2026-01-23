## 📈 Evolution & Insights

### 📅 Project Milestones

#### **v2.0 - Deep Reasoning in Vertical Domains (Current)**

**Core Philosophy:** Transition from "General Search" to "High-Precision Closed Loop."

* **Inverse Optimization:** Specifically for internal technical documentation scenarios, external web search tools (Search API) are proactively removed to prevent internet noise from diluting the precision of internal knowledge.
* **Semantic Alignment:** Strengthens the Agent's understanding of internal terminology and private architectures, ensuring all answers are verifiable and grounded (based on local Markdown indexing).
* **Orchestration Upgrade:** The `llm_planner` introduces JSON-formatted task lists, supporting complex dependency analysis to prevent logical fragmentation during multi-turn dialogues.

#### **v1.0 - Foundational ReAct Architecture**

**Core Philosophy:** Implementing the standard `Thought-Action-Observation` reasoning loop.

* **Implementation:** Developed the foundational `ReActAgent` and a simple keyword-based planner (`Simple Planner`).
* **Pain Points:**
* **Hallucination Risk:** Susceptible to calling irrelevant tools or falling into invalid infinite loops when faced with vague instructions.
* **Context Overload:** Unfiltered tool execution results (especially massive raw logs) were fed directly into the context, leading to rapid token exhaustion.



---

### 🧠 Deep Thinking: Why avoid a "Generalist" Agent?

During the development process, I discovered that **Generalist Agents suffer from significant "boundary blurring" issues when handling private technical documents**:

1. **Side Effects of External Search:** When an Agent fails to find a specific interface in internal documents, it often attempts to search the internet and returns similar open-source library solutions, which is severely misleading in enterprise-level development.
2. **Noise as Pollution:** Raw debug logs and excessively long Markdown fragments, if not processed through "semantic distillation," distract the LLM's attention and cause it to ignore truly core parameters.
3. **Certainty Over Flexibility:** In technical consultation scenarios, users require "100% accurate local information" rather than "50% accurate comprehensive descriptions."
