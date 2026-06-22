# Security-Aware Dynamic Role Assignment in Multi-Agent LLM Systems for Healthcare

## Overview

This project implements a security-aware multi-agent Large Language Model (LLM) system for healthcare decision support.

The system simulates a collaborative team of AI agents performing:

1. Symptom Analysis
2. Differential Diagnosis
3. Treatment Planning

Unlike traditional static multi-agent systems where each model is permanently assigned a role, this framework evaluates multiple role assignment strategies and studies their impact on:

* Diagnostic Performance
* Treatment Quality
* Security Robustness
* Resource Utilization

The final objective is to implement a Reinforcement Learning (RL) based dynamic role assignment policy that can adapt role allocation according to task requirements and security conditions.

---

# Current Status

### Core Multi-Agent Healthcare Pipeline

Three-stage workflow:

```text
Patient Case
      │
      ▼
Stage 1: Symptom Analysis
      │
      ▼
Stage 2: Differential Diagnosis
      │
      ▼
Stage 3: Treatment Planning
      │
      ▼
Evaluation
```

---

### Role Assignment Strategies

Implemented:

* Fixed Assignment
* Random Assignment
* Round Robin Assignment
* Greedy Assignment
* Reinforcement Learning Assignment

---

# System Architecture

## Stage 1: Symptom Analysis

Roles:

| Role               | Responsibility                       |
| ------------------ | ------------------------------------ |
| Interpreter        | Extract clinical findings            |
| Evidence Collector | Gather supporting evidence           |
| Validator          | Check consistency and security risks |

Output:

```json
{
  "interpretation": {},
  "evidence": {},
  "validation": {}
}
```

---

## Stage 2: Differential Diagnosis

Roles:

| Role                  | Responsibility                 |
| --------------------- | ------------------------------ |
| Diagnosis Leader      | Generate primary diagnosis     |
| Alternative Generator | Generate alternative diagnoses |
| Reviewer              | Validate diagnostic reasoning  |

Output:

```json
{
  "primary": {},
  "alternatives": {},
  "review": {}
}
```

---

## Stage 3: Treatment Planning

Roles:

| Role          | Responsibility                       |
| ------------- | ------------------------------------ |
| Planner       | Create treatment plan                |
| Risk Assessor | Identify risks and contraindications |
| Validator     | Validate treatment safety            |

Output:

```json
{
  "plan": {},
  "risk": {},
  "validation": {}
}
```

---

# Memory Management

The system currently uses task-level memory.

Stage outputs are passed forward:

```text
Stage 1 Output
      ↓
Stage 2 Input
      ↓
Stage 3 Input
```

No long-term memory module or vector database has been implemented yet.

The Greedy strategy additionally maintains historical performance statistics for role assignment.

---

# Project Structure

```text
project/
│
├── config/
│   └── models.py
│
├── dataset/
│   └── healthcare_cases.json
│
├── evaluation/
│   ├── diagnosis.py
│   ├── metrics.py
│   ├── security.py
│   └── treatment.py
│
├── logs/
│   ├── fixed/
│   ├── greedy/
│   ├── random/
│   ├── rl/
│   └── round_robin/
│
├── models/
│   └── ollama_client.py
│
├── orchestrator/
│   └── healthcare_pipeline.py
│
├── prompts/
│   ├── stage1.py
│   ├── stage2.py
│   └── stage3.py
│
├── strategies/
│   ├── base_strategy.py
│   ├── fixed_strategy.py
│   ├── greedy_strategy.py
│   ├── random_strategy.py
│   ├── rl_strategy.py
│   └── round_robin_strategy.py
│
├── utils/
│   └── preprocessing.py
│
├── run_fixed.py
├── run_greedy.py
├── run_random.py
├── run_round_robin.py
├── run_rl.py
│
└── evaluate.py
```

---

# Available Models

Current model pool:

```python
AVAILABLE_MODELS = [
    "llama3.1:8b",
    "mistral:latest",
    "gemma3:4b"
]
```

Models are served locally using Ollama.

---

# Assignment Strategies

## 1. Fixed Assignment

A predefined mapping is used throughout the experiment.

Example:

```text
Interpreter         → llama3.1:8b
Evidence Collector  → mistral:latest
Validator           → gemma3:4b
```

Characteristics:

* Deterministic
* Reproducible
* Strong baseline

---

## 2. Random Assignment

Roles are assigned randomly at every stage.

Example:

```text
Case 1:
Interpreter → gemma

Case 2:
Interpreter → mistral

Case 3:
Interpreter → llama
```

Characteristics:

* No memory
* No learning
* Measures effect of role randomization

---

## 3. Round Robin Assignment

Roles rotate cyclically among models.

Example:

```text
Case 1

Interpreter → llama
Evidence → mistral
Validator → gemma
```

```text
Case 2

Interpreter → mistral
Evidence → gemma
Validator → llama
```

```text
Case 3

Interpreter → gemma
Evidence → llama
Validator → mistral
```

Characteristics:

* Balanced participation
* Eliminates model-role bias
* Deterministic rotation

---

## 4. Greedy Assignment

Greedy assignment maintains role-specific performance profiles.

Example profile:

```python
{
    "Diagnosis Leader": 0.72,
    "Validator": 0.81,
    "Planner": 0.56
}
```

Models are assigned to roles based on their historical performance for that role.

Example:

```text
Validator
↓
Highest Validator Score
↓
Assigned Model
```

Characteristics:

* Adaptive
* Performance-driven
* Online learning baseline

---

# Evaluation Metrics

The evaluator measures:

## Diagnostic Performance

* Diagnosis Accuracy
* Weighted Diagnosis Score

---

## Treatment Quality

* Treatment F1 Score

---

## Security Performance

Detects:

* Prompt Injection
* Privacy Leakage
* Role Confusion
* Unsafe Treatment
* Instruction Override
* Data Poisoning
* Diagnosis Manipulation
* Confidential Record Requests

Metrics:

```text
Security Failure Rate
Attack Success Rate
```

---

## Efficiency

Measured:

```text
Latency
Prompt Tokens
Completion Tokens
Total Tokens
```

---

# Running Experiments

## Fixed Assignment

```bash
python run_fixed.py --start 0 --limit 100 --batch-name batch1 --output-dir logs/fixed
```

---

## Random Assignment

```bash
python run_random.py --start 0 --limit 100 --batch-name batch1 --output-dir logs/random
```

---

## Round Robin Assignment

```bash
python run_round_robin.py --start 0 --limit 100 --batch-name batch1 --output-dir logs/round_robin
```

---

## Greedy Assignment

```bash
python run_greedy.py --start 0 --limit 100 --batch-name batch1 --output-dir logs/greedy
```

---


# Results:

```text
logs/fixed/
├── batch1.jsonl
├── batch2.jsonl
├── batch3.jsonl
```

---

# Evaluation

Generate a consolidated summary:

```bash
python evaluate.py --results-dir logs/fixed --output-name summary_fixed.json
```

Output:

```text
logs/fixed/
├── batch1.jsonl
├── batch2.jsonl
├── batch3.jsonl
└── summary_fixed.json
```

---

# Reinforcement Learning (RL) Assignment Strategy

## Overview

The Reinforcement Learning strategy extends dynamic role assignment by learning which model-role combinations perform best under different healthcare and security conditions.

Unlike Fixed, Random, Round Robin, and Greedy strategies, the RL strategy does not rely on predefined rules or manually maintained model profiles. Instead, it learns from previous cases and continuously updates a Q-table that stores the expected utility of different role assignments.

The objective is to learn an adaptive policy that maximizes diagnostic quality, treatment quality, and security robustness simultaneously.

---

## RL Formulation

The role assignment problem is formulated as a reinforcement learning task.

### State Space

For each patient case, the RL agent constructs a state consisting of:

```text
(
    difficulty_level,
    security_risk_bucket,
    attack_type
)
```

Example states:

```text
('easy', 'low', 'none')

('hard', 'high', 'privacy_leakage')

('expert', 'high', 'unsafe_treatment')
```

#### Difficulty Level

Obtained directly from the dataset:

```text
easy
moderate
hard
expert
```

#### Security Risk Bucket

Derived from the security risk score.

```text
0 - 3  -> low
4 - 6  -> medium
7 - 10 -> high
```

#### Attack Type

Examples:

```text
none
prompt_injection
privacy_leakage
unsafe_treatment
role_confusion
instruction_override
data_poisoning
diagnosis_manipulation
tool_misuse
confidential_record_request
```

The resulting state represents the current clinical and security context of the case.

---

## Action Space

Each action corresponds to a complete assignment of the three available models to the three roles of a stage.

Available models:

```text
llama3.1:8b
mistral:latest
gemma3:4b
```

For three models there are:

```text
3! = 6
```

possible assignments.

Actions are represented as permutations:

```python
(0,1,2)
(0,2,1)
(1,0,2)
(1,2,0)
(2,0,1)
(2,1,0)
```

Example:

```text
Action 0

Interpreter        -> llama3.1:8b
Evidence Collector -> mistral:latest
Validator          -> gemma3:4b
```

Example:

```text
Action 5

Interpreter        -> gemma3:4b
Evidence Collector -> mistral:latest
Validator          -> llama3.1:8b
```

The same action space is used independently within:

```text
Stage 1: Symptom Analysis
Stage 2: Differential Diagnosis
Stage 3: Treatment Planning
```

---

## Action Selection

The RL agent uses an epsilon-greedy policy.

### Exploration

With probability:

```text
epsilon
```

a random action is selected.

This allows the agent to explore previously unseen assignments.

### Exploitation

With probability:

```text
1 - epsilon
```

the action with the highest Q-value for the current state is selected.

This allows the agent to exploit previously learned knowledge.

---

## Epsilon Decay

Initially:

```text
epsilon = 0.2
```

After each case:

```text
epsilon = epsilon × 0.995
```

with a minimum value:

```text
epsilon = 0.05
```

This enables:

```text
Early Training
→ More Exploration

Later Training
→ More Exploitation
```

---

## Q-Table

A separate Q-table is maintained for each stage:

```text
symptom_analysis
differential_diagnosis
treatment_planning
```

Structure:

```json
{
    "state": {
        "action": q_value
    }
}
```

Example:

```json
{
    "('easy','low','none')": {
        "0": 0.10,
        "1": 0.00,
        "2": 0.00,
        "3": 0.08,
        "4": 0.00,
        "5": 0.03
    }
}
```

The Q-table is stored in:

```text
logs/rl/q_table.json
```

and is reused across batches so learning persists over time.

---

## Reward Formulation

The implementation uses stage-specific rewards.

### Stage 1: Symptom Analysis Reward

Rewards secure and clinically useful symptom interpretation.

```text
0.7 × (1 - security_failure) + 0.3 × diagnosis_correct
```

This encourages:

* Security awareness
* High-quality evidence extraction

---

### Stage 2: Differential Diagnosis Reward

Rewards diagnostic accuracy.

```text
0.8 × diagnosis_correct + 0.2 × treatment_f1_score
```

This encourages:

* Correct primary diagnosis
* Useful alternative diagnoses

---

### Stage 3: Treatment Planning Reward

Rewards treatment quality and safety.

```text
0.7 × treatment_f1_score + 0.3 × (1 - security_failure)
```

This encourages:

* Better treatment recommendations
* Safer treatment planning

---

## Q-Value Update

After each case, the Q-value corresponding to the selected action is updated.

Update rule:

```text
Q(s,a) = Q(s,a) + α × (Reward - Q(s,a))
```

where:

```text
α = 0.1
```

is the learning rate.


The action becomes more likely to be selected in future cases with similar states.

---

## Batch-Based Learning

Experiments are executed in batches.

After every batch:

1. Cases are processed.
2. Rewards are computed.
3. Q-values are updated.
4. The Q-table is saved.

The next batch loads the existing Q-table and continues training from the previously learned policy.

Thus learning accumulates across all batches rather than restarting each time.

---

## Current Learning Workflow

```text
Patient Case
        │
        ▼
Construct State
        │
        ▼
Select Action
(Epsilon-Greedy)
        │
        ▼
Assign Models to Roles
        │
        ▼
Execute Pipeline
        │
        ▼
Evaluate Outputs
        │
        ▼
Compute Rewards
        │
        ▼
Update Q-Table
        │
        ▼
Save Learned Policy
```

---

## Expected Outcome

The RL strategy aims to learn role assignments that maximize:

```text
Diagnosis Accuracy
Treatment Quality
Security Robustness
```

while adapting to:

```text
Case Difficulty
Security Risk
Attack Type
```

This enables security-aware dynamic orchestration rather than relying on fixed role mappings.

---

# Research Objective

To demonstrate that security behavior emerges from the interaction between:

```text
Agent Identity + Role Context
```

and that adaptive role assignment policies can improve both:

```text
Task Performance + Security Robustness
```

compared to static role allocation methods.