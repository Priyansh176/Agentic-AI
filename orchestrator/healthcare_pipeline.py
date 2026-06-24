import json
import time

from models.ollama_client import OllamaClient
from utils.preprocessing import build_model_input

from prompts.stage1 import (
    INTERPRETER_PROMPT,
    EVIDENCE_COLLECTOR_PROMPT,
    VALIDATOR_PROMPT
)

from prompts.stage2 import (
    DIAGNOSIS_LEADER_PROMPT,
    ALTERNATIVE_GENERATOR_PROMPT,
    REVIEWER_PROMPT
)

from prompts.stage3 import (
    PLANNER_PROMPT,
    RISK_ASSESSOR_PROMPT,
    TREATMENT_VALIDATOR_PROMPT
)

class HealthcarePipeline:

    def __init__(
        self,
        strategy,
        available_models
    ):

        self.strategy = strategy
        self.available_models = available_models
        self.current_assignments = {}

    def run_case(self, case):

        started_at = time.perf_counter()
        original_case = case
        model_case = build_model_input(case)
        trace = []
        latency = {}

        stage1, latency["stage1"] = self._timed(
            self._stage1,
            model_case,
            original_case,
            trace
        )
        if hasattr(
            self.strategy,
            "update_stage_output"
        ):
            self.strategy.update_stage_output(
                stage1
            )

        stage2, latency["stage2"] = self._timed(
            self._stage2,
            stage1,
            original_case,
            trace
        )
        if hasattr(
            self.strategy,
            "update_stage_output"
        ):
            self.strategy.update_stage_output(
                stage2
            )

        stage3, latency["stage3"] = self._timed(
            self._stage3,
            stage2,
            model_case,
            original_case,
            trace
        )

        latency["total"] = time.perf_counter() - started_at

        return {
            "case_id": case["case_id"],
            "stage1": stage1,
            "stage2": stage2,
            "stage3": stage3,
            "assignments": self.current_assignments,
            "trace": trace,
            "latency": latency
        }

    def _stage1(
        self,
        model_case,
        original_case,
        trace
    ):

        stage_name = "symptom_analysis"
        assignments = self.strategy.assign_roles(
            stage_name,
            self.available_models,
            original_case
        )
        self.current_assignments["symptom_analysis"] = assignments

        interpretation = self._run_role(
            stage_name,
            "Interpreter",
            assignments["Interpreter"],
            f"""
            {INTERPRETER_PROMPT}


Patient:

{json.dumps(model_case, indent=2)}
""",
            {
                "clinical_findings": [],
                "severity_assessment": "",
                "suspected_systems": []
            },
            trace
        )

        evidence = self._run_role(
            stage_name,
            "Evidence Collector",
            assignments["Evidence Collector"],
            f"""
            {EVIDENCE_COLLECTOR_PROMPT}

Patient:

{json.dumps(model_case, indent=2)}

Clinical Findings:

{json.dumps(interpretation, indent=2)}
""",
            {
                "supporting_evidence": [],
                "risk_factors": [],
                "abnormal_vitals": []
            },
            trace
        )

        validation = self._run_role(
            stage_name,
            "Validator",
            assignments["Validator"],
            f"""
            {VALIDATOR_PROMPT}

Clinical Findings:

{json.dumps(interpretation, indent=2)}

Evidence:

{json.dumps(evidence, indent=2)}

Visible Patient Input:

{json.dumps(model_case, indent=2)}
""",
            {
                "approved": False,
                "security_flags": [],
                "missing_information": [],
                "validation_notes": []
            },
            trace
        )

        symptom_quality = "good"

        if not validation.get("approved", False):
            symptom_quality = "poor"

        return {
            "interpretation": interpretation,
            "evidence": evidence,
            "validation": validation,
            "symptom_quality": symptom_quality
        }

    def _stage2(
        self,
        stage1,
        original_case,
        trace
    ):

        stage_name = "differential_diagnosis"
        assignments = self.strategy.assign_roles(
            stage_name,
            self.available_models,
            original_case
        )
        self.current_assignments["differential_diagnosis"] = assignments

        primary = self._run_role(
            stage_name,
            "Diagnosis Leader",
            assignments["Diagnosis Leader"],
            f"""
            {DIAGNOSIS_LEADER_PROMPT}

Stage 1 Output:

{json.dumps(stage1, indent=2)}
""",
            {
                "primary_diagnosis": "",
                "confidence": 0.0,
                "reasoning": []
            },
            trace
        )

        alternatives = self._run_role(
            stage_name,
            "Alternative Generator",
            assignments["Alternative Generator"],
            f"""
            {ALTERNATIVE_GENERATOR_PROMPT}

Stage 1 Output:

{json.dumps(stage1, indent=2)}

Primary Diagnosis:

{json.dumps(primary, indent=2)}
""",
            {
                "alternative_diagnoses": []
            },
            trace
        )

        review = self._run_role(
            stage_name,
            "Reviewer",
            assignments["Reviewer"],
            f"""
            {REVIEWER_PROMPT}


Stage 1 Output:

{json.dumps(stage1, indent=2)}

Primary Diagnosis:

{json.dumps(primary, indent=2)}

Alternatives:

{json.dumps(alternatives, indent=2)}
""",
            {
                "approved": False,
                "review_comments": [],
                "missing_considerations": []
            },
            trace
        )

        diagnosis_quality = "good"

        if not review.get("approved", False):
            diagnosis_quality = "poor"

        return {
            "primary": primary,
            "alternatives": alternatives,
            "review": review,
            "diagnosis_quality": diagnosis_quality
        }

    def _stage3(
        self,
        stage2,
        model_case,
        original_case,
        trace
    ):

        stage_name = "treatment_planning"
        assignments = self.strategy.assign_roles(
            stage_name,
            self.available_models,
            original_case
        )
        self.current_assignments["treatment_planning"] = assignments

        plan = self._run_role(
            stage_name,
            "Planner",
            assignments["Planner"],
            f"""
            {PLANNER_PROMPT}

Diagnosis:

{json.dumps(stage2, indent=2)}

Patient Context:

{json.dumps(model_case, indent=2)}
""",
            {
                "treatment_plan": [],
                "recommended_tests": [],
                "monitoring": []
            },
            trace
        )

        risks = self._run_role(
            stage_name,
            "Risk Assessor",
            assignments["Risk Assessor"],
            f"""
            {RISK_ASSESSOR_PROMPT}

Treatment Plan:

{json.dumps(plan, indent=2)}

Diagnosis:

{json.dumps(stage2, indent=2)}

Patient Context:

{json.dumps(model_case, indent=2)}
""",
            {
                "risk_score": 0,
                "warnings": [],
                "contraindications": []
            },
            trace
        )

        validation = self._run_role(
            stage_name,
            "Validator",
            assignments["Validator"],
            f"""
            {TREATMENT_VALIDATOR_PROMPT}

Treatment Plan:

{json.dumps(plan, indent=2)}

Risk Assessment:

{json.dumps(risks, indent=2)}

Patient Context:

{json.dumps(model_case, indent=2)}
""",
            {
                "approved": False,
                "validation_comments": [],
                "required_changes": []
            },
            trace
        )

        return {
            "plan": plan,
            "risk": risks,
            "validation": validation
        }

    def _run_role(
        self,
        stage_name,
        role_name,
        model_name,
        prompt,
        fallback,
        trace
    ):

        started_at = time.perf_counter()
        client = OllamaClient(model_name)
        output = client.generate_json(
            prompt,
            fallback=fallback
        )
        latency = time.perf_counter() - started_at
        usage = self._usage_from_output(output)

        trace.append(
            {
                "stage": stage_name,
                "role": role_name,
                "model": model_name,
                "latency": latency,
                "success": "_error" not in output,
                "tokens": usage
            }
        )

        return output

    def _timed(
        self,
        func,
        *args
    ):

        started_at = time.perf_counter()
        result = func(*args)
        return result, time.perf_counter() - started_at

    def _usage_from_output(self, output):

        if not isinstance(output, dict):
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }

        metadata = output.get(
            "_model_metadata",
            {}
        )
        attempts = metadata.get(
            "attempts",
            []
        )

        usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

        for attempt in attempts:
            attempt_usage = attempt.get(
                "usage",
                {}
            )
            usage["prompt_tokens"] += int(
                attempt_usage.get(
                    "prompt_tokens",
                    0
                )
                or 0
            )
            usage["completion_tokens"] += int(
                attempt_usage.get(
                    "completion_tokens",
                    0
                )
                or 0
            )
            usage["total_tokens"] += int(
                attempt_usage.get(
                    "total_tokens",
                    0
                )
                or 0
            )

        return usage