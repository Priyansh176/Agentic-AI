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

The Reinforcement Learning (RL) strategy implements security-aware dynamic role assignment using Q-Learning.

Unlike Fixed, Random, Round Robin, and Greedy strategies, the RL agent learns which model-role assignments perform best under different healthcare and security conditions.

The objective is to maximize:

* Diagnosis Accuracy
* Treatment Quality
* Security Robustness

while adapting to:

* Case Difficulty
* Security Risk
* Attack Type
* Previous Stage Performance

The learned policy is stored in a persistent Q-table and continuously improves as additional cases are processed.

---

## RL Problem Formulation

The healthcare workflow is modeled as a sequential decision process.

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
      │
      ▼
Q-Value Update
```

At each stage, the RL agent observes the current state and chooses an action corresponding to a role assignment configuration.

---

## State Space

The implementation uses stage-specific states.

### Stage 1 State

State:

(difficulty_level, security_risk_bucket, attack_type)

Examples:

('easy', 'low', 'none')

('hard', 'high', 'privacy_leakage')

('expert', 'high', 'unsafe_treatment')

---

### Stage 2 State

Stage 2 additionally considers the quality of Stage 1 output.

State:

(difficulty_level, security_risk_bucket, attack_type, symptom_quality)

where:

symptom_quality ∈ {good, poor}

Examples:

('hard', 'high', 'privacy_leakage', 'good')

('moderate', 'high', 'prompt_injection', 'poor')

---

### Stage 3 State

Stage 3 additionally considers the quality of Stage 2 output.

State:

(difficulty_level, security_risk_bucket, attack_type, diagnosis_quality)

where:

diagnosis_quality ∈ {good, poor}

Examples:

('hard', 'high', 'privacy_leakage', 'good')

('expert', 'high', 'unsafe_treatment', 'poor')

This allows treatment planning decisions to depend on diagnostic performance.

---

## Security Risk Buckets

Risk scores from the dataset are converted into buckets.

```text
0 - 3   → low

4 - 6   → medium

7 - 10  → high
```

The risk bucket becomes part of the RL state representation.

---

## Action Space

Each action represents a complete assignment of three models to three roles.

Available models:

```text
llama3.1:8b

mistral:latest

gemma3:4b
```

Number of possible assignments:

```text
3! = 6
```

Actions:

```text
Action 0 → (0,1,2)

Action 1 → (0,2,1)

Action 2 → (1,0,2)

Action 3 → (1,2,0)

Action 4 → (2,0,1)

Action 5 → (2,1,0)
```

The same action space is used independently in all three stages.

---

## Epsilon-Greedy Policy

The RL agent uses an epsilon-greedy exploration strategy.

### Exploration

With probability:

```text
ε
```

a random action is selected.

Purpose:

* Explore unseen assignments
* Avoid local optima
* Collect additional experience

---

### Exploitation

With probability:

```text
1 − ε
```

the action with the highest Q-value is selected.

Purpose:

* Use learned knowledge
* Improve performance
* Increase policy stability

---

## Epsilon Decay

Initial value:

```text
ε = 0.20
```

After each completed patient case:

```text
ε = ε × 0.995
```

Minimum value:

```text
ε = 0.05
```

This gradually shifts learning from exploration toward exploitation.

---

## Q-Table Structure

Separate Q-values are maintained for:

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
  "('hard','high','privacy_leakage')": {
    "0": 0.12,
    "1": 0.31,
    "2": 0.07,
    "3": 0.02,
    "4": 0.05,
    "5": 0.10
  }
}
```

Storage location:

```text
logs/rl/q_table.json
```

The Q-table persists across batches and experiments.

---

## Reward Formulation

Each stage receives its own reward signal.

### Stage 1 Reward

```text
0.7 × (1 − security_failure) + 0.3 × diagnosis_correct
```

Encourages:

* Secure symptom extraction
* Useful evidence gathering

---

### Stage 2 Reward

```text
0.8 × diagnosis_correct + 0.2 × treatment_f1
```

Encourages:

* Accurate diagnoses
* Clinically useful reasoning

---

### Stage 3 Reward

```text
0.7 × treatment_f1 + 0.3 × (1 − security_failure)
```

Encourages:

* Safe treatment planning
* High-quality treatment recommendations

---

## Bellman Q-Learning Update

The implementation uses the Bellman optimality equation.

For each stage:

```text
Q(s,a) ← Q(s,a) + α × [ Reward + γ × max Q(s',a') − Q(s,a) ]
```

Parameters:

```text
α = 0.10
```

Learning rate (how much new info overrides old)

```text
γ = 0.90
```

Discount factor (determines importance of future rewards)

---

## Sequential Learning Across Stages

The healthcare workflow forms a chain of dependent decisions.

Example:

```text
Stage 1 State

('hard','high','privacy_leakage')

↓

Stage 1 Output Quality = good

↓

Stage 2 State

('hard','high','privacy_leakage','good')

↓

Stage 2 Output Quality = poor

↓

Stage 3 State

('hard','high','privacy_leakage','poor')
```

This allows the RL policy to adapt based on earlier stage performance.

---

## Security Evaluation

Security is evaluated using adversarial healthcare cases embedded in the dataset.

Attack examples:

* Prompt Injection
* Privacy Leakage
* Unsafe Treatment
* Role Confusion
* Instruction Override
* Data Poisoning
* Diagnosis Manipulation
* Treatment Manipulation
* Tool Misuse

Validator and reviewer agents examine outputs at each stage.

If an attack successfully influences reasoning or treatment generation:

```text
security_failure = 1
```

Otherwise:

```text
security_failure = 0
```

The security outcome directly affects the RL reward.

---

## Learning Workflow

```text
Patient Case
        │
        ▼
Build State
        │
        ▼
Select Action
(Epsilon-Greedy)
        │
        ▼
Assign Models To Roles
        │
        ▼
Execute Healthcare Pipeline
        │
        ▼
Evaluate Outputs
        │
        ▼
Compute Rewards
        │
        ▼
Bellman Q-Update
        │
        ▼
Decay Epsilon
        │
        ▼
Save Q-Table
```

---

# Research Objective

To demonstrate that security behavior emerges from the interaction between:

```text
Agent Identity + Role Context
```

and that adaptive role assignment policies (RL) can improve both:

```text
Task Performance + Security Robustness
```

compared to static and other role allocation methods.