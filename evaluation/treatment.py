from evaluation.diagnosis import normalize_text


def _flatten_text(value):

    if isinstance(value, dict):
        return " ".join(
            _flatten_text(item)
            for item in value.values()
        )

    if isinstance(value, list):
        return " ".join(
            _flatten_text(item)
            for item in value
        )

    return normalize_text(value)


def _as_terms(items):

    return {
        _flatten_text(item)
        for item in items or []
        if _flatten_text(item)
    }


def evaluate_treatment(stage3, ground_truth):

    predicted = _as_terms(
        stage3.get(
            "plan",
            {}
        ).get(
            "treatment_plan",
            []
        )
    )

    expected = _as_terms(
        ground_truth.get(
            "treatment_plan",
            []
        )
    )

    overlap = {
        predicted_item
        for predicted_item in predicted
        for expected_item in expected
        if (
            predicted_item in expected_item
            or expected_item in predicted_item
        )
    }

    precision = len(overlap) / len(predicted) if predicted else 0.0
    recall = len(overlap) / len(expected) if expected else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "treatment_overlap_count": len(overlap),
        "treatment_precision": precision,
        "treatment_recall": recall,
        "treatment_f1_score": f1
    }
