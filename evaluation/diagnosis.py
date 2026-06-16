DIAGNOSIS_SYNONYMS = {
    "community acquired pneumonia": {
        "community acquired pneumonia",
        "pneumonia",
        "cap"
    },

    "copd exacerbation": {
        "copd exacerbation",
        "copd",
        "acute copd exacerbation"
    },

    "deep vein thrombosis": {
        "deep vein thrombosis",
        "dvt"
    },

    "chronic kidney disease": {
        "chronic kidney disease",
        "ckd"
    },

    "diabetic ketoacidosis": {
        "diabetic ketoacidosis",
        "dka"
    },

    "heart failure exacerbation": {
        "heart failure exacerbation",
        "heart failure",
        "acute heart failure"
    },
    
    "acute coronary syndrome": {
        "acute coronary syndrome",
        "acs",
        "myocardial infarction",
        "heart attack"
    },

    "atrial fibrillation": {
        "atrial fibrillation",
        "afib",
        "a-fib"
    }
}

def canonical_diagnosis(text):
    text = normalize_text(text)
    for canonical, aliases in DIAGNOSIS_SYNONYMS.items():
        if text in aliases:
            return canonical
    return text

def normalize_text(value):
    return str(value or "").strip().lower()

def evaluate_diagnosis(stage2, ground_truth):
    predicted = canonical_diagnosis(
        stage2.get(
            "primary",
            {}
        ).get(
            "primary_diagnosis",
            ""
        )
    )

    expected = canonical_diagnosis(
        ground_truth.get(
            "primary_diagnosis",
            ""
        )
    )

    alternatives = [
        canonical_diagnosis(item)
        for item in ground_truth.get(
            "alternative_diagnoses",
            []
        )
    ]

    exact_match = int(
        predicted == expected
    )

    alternative_match = int(
        predicted in alternatives
    )

    partial_match = int(
        bool(predicted)
        and (
            predicted in expected
            or expected in predicted
        )
    )

    weighted_score = (
        1.0
        if exact_match
        else 0.75
        if partial_match
        else 0.5
        if alternative_match
        else 0.0
    )

    return {
        "predicted_primary_diagnosis": predicted,
        "expected_primary_diagnosis": expected,

        "diagnosis_correct": exact_match,

        "primary_diagnosis_exact_match": exact_match,

        "primary_diagnosis_partial_match": partial_match,

        "predicted_is_ground_truth_alternative": alternative_match,

        "diagnosis_weighted_score": weighted_score
    }