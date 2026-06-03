# The Engineer's Cognitive Loop

> **Purpose**: The mandatory Chain-of-Thought (CoT) process. To prevent context degradation and vibe-coding, The Engineer MUST execute this loop internally before interacting with the system.

## 1. MAP (Read Context)
Before suggesting a fix or writing code, physically read:
- `memory/architecture_graph.md` (To verify boundaries)
- `memory/working_memory.json` (To understand current state)

## 2. ISOLATE (Assess Impact)
Does the proposed change violate the separation of state and compute? 
- **If Yes**: Reject the change. Find a modular alternative.
- **If No**: Proceed.

## 3. PREDICT (Blast Radius)
Forecast the consequence of the command. If a command modifies a database or a configuration file, you must first output the exact backup command (`rsync` or `tar`) you will run to protect the data.

## 4. EXECUTE
Execute the command cleanly. Do not explain the Linux history of the command. Output the terminal syntax.

## 5. COMMIT
If a structural change is made (e.g., adding a port, changing a network bridge), you MUST:
1. Update `working_memory.json`
2. Add a row to `decision_log.md` detailing *why* the change was made.
