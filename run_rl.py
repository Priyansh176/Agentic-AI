import argparse
import json
import os

from config.models import AVAILABLE_MODELS
from evaluation.diagnosis import evaluate_diagnosis
from evaluation.security import evaluate_security
from evaluation.treatment import evaluate_treatment
from orchestrator.healthcare_pipeline import HealthcarePipeline
from strategies.rl_strategy import RLAssignmentStrategy
from evaluation.metrics import (
    evaluate_cost,
    evaluate_clinical_security_score,
    evaluate_role_coverage
)

def load_dataset(path):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

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
        evaluate_clinical_security_score(metrics)
    )

    metrics.update(
        evaluate_role_coverage(result)
    )

    metrics.update(
        evaluate_cost(result)
    )

    return metrics

def append_jsonl(path, payload):

    with open(path, "a", encoding="utf-8") as file:
        file.write(
            json.dumps(payload)
            + "\n"
        )

def run(args):

    os.makedirs(
        args.output_dir,
        exist_ok=True
    )

    output_jsonl = os.path.join(
        args.output_dir,
        f"{args.batch_name}.jsonl"
    )

    if os.path.exists(output_jsonl) and not args.resume:
        os.remove(output_jsonl)

    dataset = load_dataset(args.dataset)
    start = args.start
    if args.limit is None:
        dataset = dataset[start:]
    else:
        dataset = dataset[start:start + args.limit]

    strategy = RLAssignmentStrategy(epsilon=0.2, q_table_path="logs/rl/q_table.json")
    pipeline = HealthcarePipeline(
        strategy=strategy,
        available_models=AVAILABLE_MODELS
    )

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
            if "case_failed" not in metrics:
                strategy.learn_episode(metrics)
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

        case_metrics = record.get("metrics", {})
        print(
            (
                f"[{index}/{len(dataset)}] Finished {record['case_id']} "
                f"latency={record['latency']['total']:.2f}s "
                f"diagnosis_correct={case_metrics.get('diagnosis_correct', 0)} "
                f"clinical_score={case_metrics.get('clinical_security_score', 0.0):.3f} "
                f"security_failure={case_metrics.get('security_failure', 0)} "
                f"tokens={case_metrics.get('total_tokens', 0)}"
            ),
            flush=True
        )

    strategy.save_q_table(
        "logs/rl/q_table.json"
    )
    print("\nRL assignment experiment complete.")
    print(f"Results: {output_jsonl}")

def parse_args():

    parser = argparse.ArgumentParser(
        description="Run the rl-assignment healthcare pipeline."
    )
    parser.add_argument(
        "--dataset",
        default="dataset/healthcare_cases.json"
    )
    parser.add_argument(
        "--output-dir",
        default="logs/rl"
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
    parser.add_argument(
        "--start",
        type=int,
        default=0
    )
    parser.add_argument(
        "--batch-name",
        required=True
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(
        parse_args()
    )


# python run_rl.py --start 0 --limit 10 --batch-name test --output-dir logs/rl
