def normalize_text(value):

    return str(value or "").strip().lower()


def evaluate_diagnosis(stage2, ground_truth):

    predicted = normalize_text(
        stage2.get(
            "primary",
            {}
        ).get(
            "primary_diagnosis",
            ""
        )
    )

    expected = normalize_text(
        ground_truth.get(
            "primary_diagnosis",
            ""
        )
    )

    alternatives = [
        normalize_text(item)
        for item in ground_truth.get(
            "alternative_diagnoses",
            []
        )
    ]

    return {
        "predicted_primary_diagnosis": predicted,
        "expected_primary_diagnosis": expected,
        "diagnosis_correct": int(
            predicted == expected
        ),
        "primary_diagnosis_exact_match": int(
            predicted == expected
        ),
        "primary_diagnosis_partial_match": int(
            bool(predicted)
            and (
                predicted in expected
                or expected in predicted
            )
        ),
        "predicted_is_ground_truth_alternative": int(
            predicted in alternatives
        )
    }
