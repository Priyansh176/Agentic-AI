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

## Implemented

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

Planned:

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

# Future Work: Reinforcement Learning Assignment

The final stage of the project is an RL-based dynamic role assignment framework.

Goal:

```text
Learn optimal role assignments
instead of using predefined rules.
```

---

## RL Formulation

### State

Potential state features:

* Case difficulty
* Security risk score
* Attack type
* Historical model performance
* Previous rewards
* Diagnostic complexity

---

### Action

Assign models to roles.

Example:

```text
Interpreter → Model A
Evidence Collector → Model B
Validator → Model C
```

---

### Reward

Combination of:

```text
+ Diagnosis Accuracy
+ Treatment Quality
+ Security Robustness

- Security Failures
- Latency
```

---

### Expected Benefits

Compared to Fixed, Random, Round Robin, and Greedy:

* Better diagnostic performance
* Lower attack success rate
* Improved treatment quality
* Adaptive security-aware orchestration

---

# Research Objective

To demonstrate that security behavior emerges from the interaction between:

```text
Agent Identity
+
Role Context
```

and that adaptive role assignment policies can improve both:

```text
Task Performance
+
Security Robustness
```

compared to static role allocation methods.