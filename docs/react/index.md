# 🧠 ReAct Engine

The project implements the standard **ReAct (Reasoning + Acting)** paradigm, empowering the Agent to solve complex problems through a `Thought-Action-Observation` closed loop.

---

## 🛠️ Core Logic

### 1. Hybrid Planner

To balance speed and depth, the system provides two scheduling strategies for tasks of varying complexity:

* **Simple Planner**: Triggered by rules and keywords, suitable for high-frequency, deterministic tool-calling scenarios (e.g., mathematical calculations, basic index retrieval).
* **LLM Planner**: Based on large language models to generate dynamic JSON task lists, supporting multi-step logic decomposition, long-chain task orchestration, and dynamic goal adjustment.

### 2. Adaptive Reasoning Loop

Constructs a robust reasoning loop to ensure the generation process is transparent and controllable:

* **Streaming Reasoning**: Real-time output of the `Thought` process via `run_stream()`, eliminating user wait anxiety and enhancing the interaction experience.
* **Safety Guard**: Built-in `Max Iterations` limit (default: 10) to prevent the model from falling into logical infinite loops when processing vague instructions.
* **Termination Signal Convergence**: Compatible with the `Final Answer` keyword and `Action: FINISH` command, ensuring the Agent converges accurately upon task completion.

### 3. Executor Sandbox

Provides a secure execution environment and error tolerance mechanism for tool calls:

* **Role-Based Access Control (RBAC)**: Strictly controls the Agent's operational boundaries via `allowed_tools` to prevent unauthorized calls to sensitive tools at the foundational level.
* **Robust Execution Mechanism**:
* **Auto-Retry**: Built-in exponential backoff retry mechanism for LLM calls (up to 3 times).
* **Exception Handling**: Semantic wrapping of tool-returned errors, feeding error information back to the model for self-correction rather than a direct crash.
