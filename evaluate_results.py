import argparse
import json
import os

from evaluation.metrics import summarize


def load_jsonl(path):

    records = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if line:

                records.append(
                    json.loads(line)
                )

    return records


def collect_results(root_dir):

    all_records = []

    for root, _, files in os.walk(root_dir):

        for filename in files:

            if filename.endswith(".jsonl"):

                path = os.path.join(
                    root,
                    filename
                )

                print(
                    f"Loading {path}"
                )

                all_records.extend(
                    load_jsonl(path)
                )

    return all_records


def run(args):

    records = collect_results(
        args.input_dir
    )

    print(
        f"Loaded {len(records)} records"
    )

    summary = summarize(records)

    output_file = os.path.join(
        args.input_dir,
        "final_summary.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=2
        )

    print(
        f"Summary written to {output_file}"
    )


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-dir",
        required=True
    )

    return parser.parse_args()


if __name__ == "__main__":
    run(
        parse_args()
    )