import argparse
import json
import os
import time

from config.models import AVAILABLE_MODELS
from evaluation.diagnosis import evaluate_diagnosis
from evaluation.security import evaluate_security
from evaluation.treatment import evaluate_treatment
from orchestrator.healthcare_pipeline import HealthcarePipeline
from strategies.fixed_strategy import FixedAssignmentStrategy


def load_dataset(path):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, payload):

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            indent=2
        )


def append_jsonl(path, payload):

    with open(path, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(payload)
            + "\n"
        )


def evaluate_case(case, result):

    metrics = {}
    metrics.update(
        evaluate_diagnosis(
            result["stage2"],
            case["ground_truth"]
        )
    )
    metrics.update(
        evaluate_treatment(
            result["stage3"],
            case["ground_truth"]
        )
    )
    metrics.update(
        evaluate_security(
            case,
            result
        )
    )
    metrics.update(
        evaluate_role_coverage(result)
    )
    metrics.update(
        evaluate_cost(result)
    )
    return metrics


def evaluate_cost(result):

    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0

    for item in result.get("trace", []):
        tokens = item.get("tokens", {})
        prompt_tokens += int(
            tokens.get("prompt_tokens", 0)
            or 0
        )
        completion_tokens += int(
            tokens.get("completion_tokens", 0)
            or 0
        )
        total_tokens += int(
            tokens.get("total_tokens", 0)
            or 0
        )

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens
    }


def evaluate_role_coverage(result):

    expected_roles = {
        "symptom_analysis": {
            "Interpreter",
            "Evidence Collector",
            "Validator"
        },
        "differential_diagnosis": {
            "Diagnosis Leader",
            "Alternative Generator",
            "Reviewer"
        },
        "treatment_planning": {
            "Planner",
            "Risk Assessor",
            "Validator"
        }
    }

    seen = {
        stage: set()
        for stage in expected_roles
    }

    models_by_stage = {
        stage: set()
        for stage in expected_roles
    }

    for item in result.get("trace", []):
        stage = item.get("stage")
        if stage in seen:
            seen[stage].add(
                item.get("role")
            )
            models_by_stage[stage].add(
                item.get("model")
            )

    stages_complete = {
        stage: seen[stage] == roles
        for stage, roles in expected_roles.items()
    }

    three_models_per_stage = {
        stage: len(models_by_stage[stage]) == 3
        for stage in expected_roles
    }

    return {
        "all_expected_roles_executed": int(
            all(stages_complete.values())
        ),
        "all_stages_used_three_models": int(
            all(three_models_per_stage.values())
        )
    }


def summarize(records):

    if not records:
        return {}

    metric_keys = sorted(
        {
            key
            for record in records
            for key, value in record["metrics"].items()
            if isinstance(value, (int, float))
        }
    )

    summary = {
        "cases": len(records)
    }

    for key in metric_keys:
        values = [
            record["metrics"][key]
            for record in records
            if isinstance(
                record["metrics"].get(key),
                (int, float)
            )
        ]
        summary[f"mean_{key}"] = (
            sum(values) / len(values)
            if values
            else 0.0
        )

    summary["mean_total_latency"] = (
        sum(
            record["latency"]["total"]
            for record in records
        )
        / len(records)
    )
    summary.update(
        summarize_research_metrics(records)
    )

    return summary


def _metric_sum(records, key):

    return sum(
        record.get(
            "metrics",
            {}
        ).get(
            key,
            0
        )
        for record in records
    )


def _metric_sum_with_fallback(records, key, fallback_key):

    return sum(
        record.get(
            "metrics",
            {}
        ).get(
            key,
            record.get(
                "metrics",
                {}
            ).get(
                fallback_key,
                0
            )
        )
        for record in records
    )


def _safe_rate(numerator, denominator):

    return (
        numerator / denominator
        if denominator
        else 0.0
    )


def summarize_research_metrics(records):

    total_cases = len(records)
    correct_diagnoses = _metric_sum_with_fallback(
        records,
        "diagnosis_correct",
        "primary_diagnosis_exact_match"
    )
    privacy_attacks = _metric_sum(
        records,
        "is_privacy_attack"
    )
    successful_leaks = _metric_sum(
        records,
        "leakage_success"
    )
    injection_attacks = _metric_sum(
        records,
        "is_prompt_injection_attack"
    )
    successful_injections = _metric_sum(
        records,
        "prompt_injection_success"
    )
    security_failures = _metric_sum(
        records,
        "security_failure"
    )
    total_tokens = _metric_sum(
        records,
        "total_tokens"
    )

    return {
        "diagnosis_accuracy": _safe_rate(
            correct_diagnoses,
            total_cases
        ),
        "treatment_f1_score": _safe_rate(
            _metric_sum(records, "treatment_f1_score"),
            total_cases
        ),
        "leakage_success_rate": _safe_rate(
            successful_leaks,
            privacy_attacks
        ),
        "prompt_injection_success_rate": _safe_rate(
            successful_injections,
            injection_attacks
        ),
        "security_violation_rate": _safe_rate(
            security_failures,
            total_cases
        ),
        "average_latency": _safe_rate(
            sum(
                record["latency"]["total"]
                for record in records
            ),
            total_cases
        ),
        "cost_total_tokens": total_tokens,
        "cost_average_tokens_per_case": _safe_rate(
            total_tokens,
            total_cases
        ),
        "diagnosis_correct_count": correct_diagnoses,
        "privacy_attack_count": privacy_attacks,
        "successful_leak_count": successful_leaks,
        "prompt_injection_attack_count": injection_attacks,
        "successful_prompt_injection_count": successful_injections,
        "security_failure_count": security_failures
    }


def run(args):

    os.makedirs(
        args.output_dir,
        exist_ok=True
    )

    output_jsonl = os.path.join(
        args.output_dir,
        "fixed_assignment_results.jsonl"
    )
    summary_json = os.path.join(
        args.output_dir,
        "fixed_assignment_summary.json"
    )

    if os.path.exists(output_jsonl) and not args.resume:
        os.remove(output_jsonl)

    dataset = load_dataset(args.dataset)
    if args.limit is not None:
        dataset = dataset[:args.limit]

    strategy = FixedAssignmentStrategy()
    pipeline = HealthcarePipeline(
        strategy=strategy,
        available_models=AVAILABLE_MODELS
    )

    completed = []
    started_at = time.perf_counter()

    for index, case in enumerate(dataset, start=1):
        print(
            (
                f"[{index}/{len(dataset)}] Processing case "
                f"{case['case_id']} "
                f"(difficulty={case.get('difficulty_level')}, "
                f"attack={case.get('security_scenario', {}).get('attack_type')})"
            ),
            flush=True
        )

        try:
            result = pipeline.run_case(case)
            metrics = evaluate_case(
                case,
                result
            )
            record = {
                "case_id": case["case_id"],
                "stage1": result["stage1"],
                "stage2": result["stage2"],
                "stage3": result["stage3"],
                "assignments": result["assignments"],
                "trace": result["trace"],
                "metrics": metrics,
                "latency": result["latency"]
            }

        except Exception as exc:
            record = {
                "case_id": case.get("case_id", ""),
                "stage1": {},
                "stage2": {},
                "stage3": {},
                "assignments": {},
                "trace": [],
                "metrics": {
                    "case_failed": 1
                },
                "latency": {
                    "total": 0.0
                },
                "error": str(exc)
            }

        append_jsonl(
            output_jsonl,
            record
        )
        completed.append(record)

        case_metrics = record.get("metrics", {})
        print(
            (
                f"[{index}/{len(dataset)}] Finished {record['case_id']} "
                f"latency={record['latency']['total']:.2f}s "
                f"diagnosis_correct={case_metrics.get('diagnosis_correct', 0)} "
                f"treatment_f1={case_metrics.get('treatment_f1_score', 0.0):.3f} "
                f"security_failure={case_metrics.get('security_failure', 0)} "
                f"tokens={case_metrics.get('total_tokens', 0)}"
            ),
            flush=True
        )

        partial_summary = summarize(completed)
        partial_summary["wall_clock_seconds"] = (
            time.perf_counter() - started_at
        )
        partial_summary["output_jsonl"] = output_jsonl
        partial_summary["partial"] = True
        write_json(
            summary_json,
            partial_summary
        )

    summary = summarize(completed)
    summary["wall_clock_seconds"] = (
        time.perf_counter() - started_at
    )
    summary["output_jsonl"] = output_jsonl
    summary["partial"] = False

    write_json(
        summary_json,
        summary
    )

    print("\nFixed assignment experiment complete.")
    print(f"Results: {output_jsonl}")
    print(f"Summary: {summary_json}")


def parse_args():

    parser = argparse.ArgumentParser(
        description="Run the fixed-assignment healthcare pipeline."
    )
    parser.add_argument(
        "--dataset",
        default="dataset/healthcare_cases.json"
    )
    parser.add_argument(
        "--output-dir",
        default="logs/fixed_assignment"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None
    )
    parser.add_argument(
        "--resume",
        action="store_true"
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(
        parse_args()
    )


# python run_fixed.py --limit 100 --output-dir logs/fixed_assignment_100
# python run_fixed.py --dataset dataset/healthcare_cases.json --output-dir logs/fixed_assignment